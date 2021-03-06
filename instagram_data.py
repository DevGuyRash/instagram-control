import requests
from bs4 import BeautifulSoup
from file_manager import FileManager
from instagram_scraper import InstagramScraper
import re
import json
import os
from datetime import datetime


class InstagramPage:

    def __init__(self, instagram_json):
        self.page = instagram_json


class User:
    """
    Class meant to hold all info related to an instagram user.

    Args:
        username (str): Username of instagram account.
        json_data (dict): Json data returned from Instagram api about
            a user.
            Api endpoint:
                https://i.instagram.com/api/v1/users/web_profile_info/
            Api params:
                username (str): username of instagram account to search.

    Attributes:
        username (str): Username of instagram account.
        is_private (bool): Whether the instagram account is private or
            not.
        is_verified (bool): Whether the instagram account is verified or
            not.
        is_business_account (bool): Whether the instagram account is
            a business account or not.
        is_professional_account (bool): Whether the instagram account is
            a business account or not.
        name (str): Full name on the instagram account.
        id (str): Unique ID of the instagram account.
        facebook_id (str): Unique Facebook ID of the instagram account.
        bio (str): Instagram Account's biography.
        bio_entities (dict): Contains any hashtags or other accounts
            referenced in the `bio`.
        website (str): Website associated with the instagram account.
        followers (str): How many followers the instagram account has.
        following (str): How many people are following the instagram
            account.
        category (str): Which category instagram puts this account into.
        pronouns (str): Custom pronouns the user has chosen for the
            instagram account.
        is_recent (bool): Whether the instagram account was recently
            created or not.
        total_timeline_posts (str): Total amount of posts on the
            instagram account's main timeline.
        total_video_posts (str): Total amount of video posts on the
            instagram account's video timeline.
        profile_pic (str): URL leading to the account's profile picture
            resource.
        profile_pic_hd (str): URL leading to a higher resolution picture
            of the account's profile.
        business_address (str): Business address associated with the
            instagram account.
        business_email (str): Business email associated with the
            instagram account.
        business_phone (str): Business phone number associated with the
            instagram account.
        business_category (str): Which category instagram puts this
            account into, business-wise.
        facebook_page (str): Facebook page associated with this
            instagram account.
    """

    def __init__(self, username: str, json_data: dict):
        self.username = username

        # Save json_data to a file for logging. Must be after username assignment.
        self.save(json_data)
        # Create base index path to get the rest of the data from
        base = json_data["data"]["user"]

        # Account status checks
        self.is_private = base.get('is_private')
        self.is_verified = base.get('is_verified')
        self.is_business_account = base.get('is_business_account')
        self.is_professional_account = base.get('is_professional_account')

        # Basic account info
        self.name = base.get('full_name')
        self.id = base.get('id')
        self.facebook_id = base.get('fbid')
        self.bio = base.get('biography')
        self.bio_entities = base.get('biography_with_entities').get('entities')
        self.website = base.get('external_url')
        self.followers = base['edge_followed_by'].get('count')
        self.following = base['edge_follow'].get('count')
        self.category = base.get('category_name')  # What type of account is this
        self.pronouns = base.get('pronouns')
        self.is_recent = base["is_joined_recently"]

        # Posts
        timeline_posts = base["edge_owner_to_timeline_media"]
        video_posts = base["edge_felix_video_timeline"]

        self.total_timeline_posts = timeline_posts.get('count')
        self.total_video_posts = video_posts.get('count')

        # profile pic
        self.profile_pic = base.get('profile_pic_url')
        self.profile_pic_hd = base.get('profile_pic_url_hd')

        # Business account info
        self.business_address = base.get('business_address_json')
        self.business_email = base.get('business_email')
        self.business_phone = base.get('business_phone_number')
        self.business_category = base.get('business_category_name')
        self.facebook_page = base["connected_fb_page"]

    def __str__(self):
        return f"Id: {self.id}\n" \
               f"Username: {self.username}\n" \
               f"Full Name: {self.name}\n" \
               f"Followers: {self.followers} | Following: {self.following}\n" \
               f"Category: {self.category}\n" \
               f"Website: {self.website}\n" \
               f"Bio: {self.bio}"

    def save(self, json_data):
        FileManager.create_dir("json/users")

        # Save json data to a file.
        with open(f"json/users/{self.username}.json", 'w', encoding='utf-8') as file:
            json.dump(json_data, file)


class Post:
    """
    Class containing all information about an Instagram post.

    Save comments that are found on a post into a list, but does not
    save all of them. It will only save the ones that are returned via
    the instagram post api.

    Args:
        json_data (dict): Json data returned from Instagram api about
            a user's post. The media id must be used inside the
            endpoint. There are no _parameters.
            Api endpoint:
                https://i.instagram.com/api/v1/media/`MEDIA_ID`/info

    Attributes:
        access_caption (str): The accessibility caption associated with
            the post, if there is one.
        caption (Comment): The caption of the post, made by the poster.
        comments (dict[str: Comment]): `list` of comments contained inside
            the post.
        comments_disabled (bool): Whether comments are disabled o not.
        comment_likes_enabled (bool): Whether comment likes_total are
            enabled or not.
        comments_total (str): Total amount of comments on the post.
        created (int): Timestamp of when the post was created
        created_formatted (datetime): `Datetime` object of when the post
            was created.
        duration (int): Length of video. Applies to single media video
            posts.
        id (str): Unique id associated with the post.
        likes (dict): Contains all users found that liked the post.
        likes_and_views_disabled (bool): Whether the likes_total and view
            counts are disabled or not.
        likes_total (str): Total amount of likes_total on the post.
        media (list): Contains `Media` objects of all media in the post.
        media_count (int): Total amount of media in the post. Applies to
            carousel media when there are multiple images or videos in
            a single post.
        media_type (int): Format of the media in the post (different
            numbers meaning photo, video, gif, etc.)
        name (str): Full name of the account that created the post.
        pk (str): Unique id associated with the post.
        short_code (str): Unique url id used to access this post, usually
        username (str): Username of the account that posted this post.
        users_tagged (list): List of users tagged in this post.
            found towards the end of the url when you are on the post.
        views_total (int): Total amount of views on the post. Applies to
            single media video posts.
    """

    def __init__(self, json_data):
        # Create base index path to get the rest of the data from
        try:
            base = json_data["items"][0]
        except KeyError:
            # If json_data is not a valid instagram json from the api, it won't
            # have "items" key. So it's invalid.
            print("Invalid instagram post, skipping...")
            return

        # short_code and username must be assigned before saving.
        # Use the short_code with the user-post link in urls to go to the post.
        self.short_code = base.get('code')

        # Poster info
        self.username = base["user"]["username"]
        self.name = base["user"]["full_name"]

        # Save json_data to a file for logging
        self.save(json_data)

        # Post media info - Important as some attributes will or won't be
        # available depending on the type.
        self.media_type = base.get('media_type')
        self.media_count = 1
        self.media = []
        # Media ID's unique to this post
        self.pk = base.get('pk')
        self.id = base.get('id')

        # For video posts
        self.views_total = base.get("view_count")
        self.duration = base.get("video_duration")

        if self.media_type == 8:
            # Carousel multi video / photo post
            self.media_count = base['carousel_media_count']
            for media in base['carousel_media']:
                # Create base index routes
                media_type = media["media_type"]
                if media_type == 1:
                    # The current media is a photo
                    media_info = media["image_versions2"]["candidates"][0]
                else:
                    # The current media is a video
                    media_info = media["video_versions"][0]

                # Create Media object and append to media list
                self.media.append(Media(
                    media_type=media_type,
                    pk=media['pk'],
                    original_width=media['original_width'],
                    original_height=media['original_height'],
                    width=media_info["width"],
                    height=media_info["height"],
                    url=media_info["url"],
                    thumbnail_url=media['image_versions2']['candidates'][0]['url'],
                    duration=media.get('video_duration'),
                    dash_manifest=media.get('video_dash_manifest'),
                    codec=media.get('video_codec'),
                ))
        else:
            # Single photo / video post
            if self.media_type == 1:
                # Image
                media_info = base['image_versions2']['candidates'][0]
            else:
                # Video
                media_info = base['video_versions'][0]

            # Create Media object and append to media list
            self.media.append(Media(
                media_type=self.media_type,
                pk=self.pk,
                original_width=base['original_width'],
                original_height=base['original_height'],
                width=media_info["width"],
                height=media_info["height"],
                url=media_info["url"],
                thumbnail_url=base['image_versions2']['candidates'][0]['url'],
                duration=base.get('video_duration'),
                dash_manifest=base.get('video_dash_manifest'),
                codec=base.get('video_codec'),
            ))

        # Perform checks on post to verify data retrieval
        self.likes_and_views_disabled = base.get('like_and_view_counts_disabled')
        self.comment_likes_enabled = base.get('comment_likes_enabled')  # Not in multi-video

        # Only present in photos (media type 1)
        self.access_caption = base.get('accessibility_caption')

        # Only found in non-carousel posts (media type 8 are carousel)
        usertags = base.get('usertags')
        if usertags:
            self.users_tagged = [username["user"]["username"]
                                 for username in base["usertags"]["in"]]
        else:
            self.users_tagged = []

        # Creation time
        self.created = base.get('taken_at')
        self.created_formatted = datetime.fromtimestamp(self.created)

        # Post metrics
        self.likes_total = base.get("like_count")
        # Will not appear if comments are disabled
        self.comments_total = base.get("comment_count")

        # Check that the post has user likes, and if so save them to the
        # instance of the Post object using a list comprehension.
        self.likes = base.get("likers", {})
        if self.likes:
            self.likes = {user["username"]: None for user in self.likes}

        # Comments
        self.comments_disabled = base.get("comments_disabled")

        # Check that the post has comments, and if so save them to the
        # instance of the Post object using a dict comprehension.
        if not self.comments_disabled:
            self.comments = {comment['user']['username']: Comment(
                username=comment['user']['username'],
                name=comment['user']['full_name'],
                text=comment['text'],
                created=comment['created_at'],
                pk=comment['pk'],
                user_id=comment['user_id'],
                media_type=comment['type'],
                likes_total=comment['comment_like_count']
            )
                for comment in base['comments']
            }
        else:
            self.comments = {}

        # Post caption
        caption = base.get('caption')
        # Create Comment object from caption to display organized info
        if caption:
            self.caption = Comment(
                username=self.username,
                name=self.name,
                pk=self.pk,
                user_id=self.id,
                text=caption.get('text'),
                created=caption.get('created_at_utc'),
            )
        else:
            # If there is no caption, then create an empty Comment object to
            # preserve polymorphism.
            self.caption = Comment(
                username=self.username,
                name=self.name,
                text="",
                created=0
            )

    def __str__(self):
        return f"Post ID: {self.id}\n" \
               f"Post URL_ID: {self.short_code}\n" \
               f"Post By: {self.username}\n" \
               f"Post Caption: {self.caption.text}\n" \
               f"Post Total Likes: {self.likes_total}\n" \
               f"Post Total Comments: {self.comments_total}\n" \
               f"Post Created on: {self.created_formatted}"

    def save(self, json_data):
        # Create json folder, if it doesn't already exist.
        try:
            os.mkdir(os.path.abspath("json"))
        except FileExistsError:
            pass

        # Create posts folder, if it doesn't already exist.
        try:
            os.mkdir(f'{os.path.abspath("json")}/posts')
        except FileExistsError:
            pass

        FileManager.create_dir("json/posts")
        # Save the json file
        with open(f"json/posts/{self.username}_post_{self.short_code}.json", 'w',
                  encoding='utf-8') as file:
            json.dump(json_data, file)


class Comment:
    """
    Class to contain info about an instagram comment.

    Args:
        username (str): Username of the account that posted the comment.
        name (str): Full name of the account that posted the comment.
        text (str): The text of the comment
        created (int): Timestamp of when the comment was created.
        pk (str): Unique id associated with the comment.
        user_id (int): Unique id associated with the comment author.
        media_type (int): Format of the media in the comment. The number
            represents video, text, image, etc.
        likes_total (int): Total amount of likes_total on the comment.

    Attributes:
        username (str): Username of the account that posted the comment.
        name (str): Full name of the account that posted the comment.
        text (str): The text of the comment
        created (int): Timestamp of when the comment was created.
        created_formatted (datetime): `Datetime` object of when the
            comment was created.
        pk (str): Unique id associated with the comment.
        user_id (int): Unique id associated with the comment author.
        media_type (int): Format of the media in the comment. The number
            represents video, text, image, etc.
        likes_total (int): Total amount of likes_total on the comment.
        user (User): Optional `User` object attached to the comment for
            more information.
    """

    def __init__(self,
                 username: str,
                 name: str,
                 text: str,
                 created: int,
                 pk: str = "",
                 user_id: int = 0,
                 media_type: int = 0,
                 likes_total: int = 0,
                 user: User = None
                 ):
        self.username = username
        self.name = name
        self.text = text
        self.created = created
        self.created_formatted = datetime.fromtimestamp(self.created)
        self.pk = pk
        self.user_id = user_id
        self.media_type = media_type
        self.likes_total = likes_total
        self.user = user

    def __str__(self):
        return f"Comment: {self.text}\n" \
               f"Comment By {self.name} / @{self.username}, " \
               f"on {self.created_formatted}\n" \
               f"Comment Likes: {self.likes_total or 'Does not apply to captions.'}"


class Media:
    """
    Class to contain media info such as type, dimensions, and urls.

    Args:
        media_type (int): Format of media:
            0 = Text
            1 = Photo
            2 = Video
            8 = carousel
        pk (str): Unique id associated with the media.
        original_width (int): Width of the photo or video before
            instagram compressed it.
        original_height (int): Height of the photo or video before
            instagram compressed it.
        width (int): Width of the photo or video.
        height (int): Height of the photo or video.
        url (str): Url leading to where the media is stored.
        thumbnail_url (str): Url leading to where the video thumbnail is
            stored when the media is a video.

    Attributes:
        media_type (int): Format of media:
            0 = Text
            1 = Photo
            2 = Video
            8 = carousel
        type (str): `Photo` if `media_type` is 1, or `Video` if
            `media_type`is 2.
        id (str): Unique id associated with the media.
        pk (str): Unique id associated with the media.
        original_width (int): Width of the photo or video before
            instagram compressed it.
        original_height (int): Height of the photo or video before
            instagram compressed it.
        width (int): Width of the photo or video.
        height (int): Height of the photo or video.
        url (str): Url leading to where the media is stored.
        thumbnail_url (str): Url leading to video thumbnail if it's a
            video, else it leads to `url`.
        duration (float): Length of video. If it's a photo, it will
            default to `0`.
        codec (str): Codec of the video. Does not apply to a photo.
        dash_manifest (str): Information specific to a video. Does not
            apply to a photo.
        has_audio (bool): Whether a video has audio or not. Does not
            apply to a photo.
    """

    def __init__(self,
                 media_type: int,
                 pk: str,
                 original_width: int,
                 original_height: int,
                 width: int,
                 height: int,
                 url: str,
                 thumbnail_url: str = "",
                 duration: float = 0.0,
                 codec: str = "",
                 dash_manifest: str = "",
                 has_audio: bool = False,
                 ):
        self.media_type = media_type
        # ID is the same as pk here
        self.id = pk
        self.pk = pk
        self.original_width = original_width
        self.original_height = original_height
        self.width = width
        self.height = height
        self.url = url
        self.duration = duration
        self.codec = codec
        self.dash_manifest = dash_manifest
        self.has_audio = has_audio

        # Type specific changes:
        if self.media_type == 1:
            # Photo
            self.type = "Photo"
            self.thumbnail_url = self.url
        else:
            # Video
            self.type = "Video"
            self.thumbnail_url = thumbnail_url

    def __str__(self):
        if self.media_type == 1:
            return f"ID: {self.id}\n" \
                   f"Media Type: {self.media_type} | {self.type}\n" \
                   f"Dimensions: {self.width}x{self.height}\n" \
                   f"URL: {self.url}\n"
        else:
            return f"ID: {self.id}\n" \
                   f"Media Type: {self.media_type} | {self.type}\n" \
                   f"Dimensions: {self.width}x{self.height}\n" \
                   f"URL: {self.url}\n" \
                   f"Thumbnail: {self.thumbnail_url}\n" \
                   f"Duration: {self.duration}\n" \
                   f"Audio: {self.has_audio}\n" \
                   f"Codec: {self.codec}"


class Hashtag:

    def __init__(self, hashtag):
        self.text = hashtag
        # self.geo_checker = Geometry()


class HashtagManager:

    def __init__(self):
        pass


class UserManager:
    with open("urls.json", encoding='utf-8') as f:
        URLS = json.load(f)["instagram"]

    def __init__(self):
        pass

    @staticmethod
    def create_users(session: requests.Session, user: "", *args, **kwargs) -> list:
        """
        Searches up usernames given by the user, on Instagram.

        Will retrieve the json data per user given, and create a `User`
        object for each. All users will be appended to `users`
        attribute in a list.

        Args:
            session: Requests `Session` or similar object.
            user: Single username to search up, rather than getting
                input.
            *args: Any additional arguments to apply to the session GET.
            **kwargs: Any additional arguments to apply to the session
                GET.
        """
        # List where User objects will be stored, and return value
        list_of_users = []
        if not user:
            # List of usernames to research
            usernames = []
            print("Please input usernames to pull.")
            print("Type 'e' when you are finished entering usernames.")
            while True:
                # Get user input
                username = "".join(input(">").casefold().split())

                # Break out of loop if user wants to
                if username == "e":
                    break

                usernames.append(username)

        else:
            # Single user is to be searched up
            usernames = [user]

        for user in usernames:
            # Pull each username in the above list
            params = {
                "username": user,
            }

            # Get username info
            response = session.get(UserManager.URLS["user-profile"],
                                   params=params, *args, **kwargs)
            # If the user is found
            if response.status_code == 200:
                data = response.json()

                # Create User
                new_user = User(username=user, json_data=data)
                list_of_users.append(new_user)

                print(f"'{user} has been found!")
            else:
                # If the username does not exist
                print(f"Username '{user}` not found!")

        print("Account search complete.")

        return list_of_users


class PostManager:
    with open("urls.json", encoding='utf-8') as f:
        URLS = json.load(f)["instagram"]

    def __init__(self, session):
        self.session = session
        self.posts = []

    def get_user_posts(self, *args, **kwargs) -> None:
        """
        Retrieves the json data for multiple user inputted posts.

        Converts all users that commented and liked the post into `User`
        objects.

        Args:
            *args: Additional arguments to pass to the `GET` request
                of instance `session`.
            **kwargs: Additional arguments to pass to the `GET` request
                of instance `session`.
        """
        print(f"Input instagram post url codes, or full URLs "
              f"(format: {PostManager.URLS['user-post']}[URL_CODE]/)")
        print("When you're finished inputting Posts to get, type 'e'")
        posts_to_get = []
        posts = []
        while True:
            # Create list of posts to inspect from userinput
            user_post = "".join(input(">").split())
            # If user is finished adding posts
            if user_post == "e":
                break

            posts_to_get.append(user_post)

        for user_post in posts_to_get:
            # Only take the last part of the url, the actual post code.
            url_code = re.search('/*([a-zA-Z0-9-_]+)/*$', user_post)
            if url_code:
                # A match was found, so get the match
                url_code = url_code.group(1)
                params = {
                    "can_support_threading": "true",
                    "permalink_enabled": "false",
                }
                converted_post = Post(self.get_post_data(url_code,
                                                         *args,
                                                         params=params,
                                                         **kwargs))
                # Convert all usernames found in post's likes into User
                # objects.
                if converted_post.likes:
                    # Create a User object for all existing likes.
                    # Index to 0 as a list is returned by create_users.
                    for user in converted_post.likes:
                        converted_post.likes[user] = UserManager.create_users(
                            user=user,
                            session=self.session,
                        )[0]

                if converted_post.comments:
                    # There's comments on the post
                    for comment in converted_post.comments:
                        if comment.username in converted_post.likes:
                            # There already exists a user object for this username
                            comment.user = converted_post.likes[comment.username]
                        else:
                            # Create a new User for this comment
                            comment.user = UserManager.create_users(
                                user=comment.username,
                                session=self.session,
                            )[0]

                posts.append(converted_post)

        self.posts = posts

    def get_post_data(self, short_code: str, *args, **kwargs) -> dict:
        """
        Gets the `json` data from an instagram post.

        Will accept any instagram post url code, which is normally
        random letters and numbers:
            https://www.instagram.com/p/[URL_CODE]/

        Examples:
            get_post_data(url_code="CCeGDPkDWJ4/")

        Args:
            short_code: Unique shortcode for the instagram post, usually
                located near the end of the URL.
            *args: Any additional arguments to apply to the session GET.
            **kwargs: Any additional arguments to apply to the session
                GET.

        Returns:
            `dict` containing all information about the instagram post.
        """
        # Get the html of the post page to ge the media_id
        response = self.session.get(f"{self.URLS['user-post']}{short_code}", *args, **kwargs)
        # Get media id from html
        media_id = self.extract_id_from_post(response.text)

        # Return info about the post
        return self.session.get(f"{self.URLS['user-post-api']}"
                                f"{media_id}/"
                                f"{self.URLS['user-post-api-end']}",
                                *args,
                                **kwargs).json()

    @staticmethod
    def extract_id_from_post(post_html: str) -> str:
        """
        Extracts the `media_id` from the html of an instagram post.

        Format of the instagram post url to extract the html from should
        be:
        https://www.instagram.com/p/[POST_CODE]

        Each post will have a shorthand code at the end.

        Args:
            post_html: Html code of the post page itself.

        Returns:
            `media_id` if found, else an empty string.
        """
        soup = BeautifulSoup(post_html, features='lxml')
        media_id = ""
        # The media_id will temporarily load under a script. Find it using
        # regular expressions
        for single_string in [script_strings for script in soup.find_all("script")
                              for script_strings in script.stripped_strings]:
            media_id = re.search('media_id":"(\d+)"', single_string)
            # If the regular expression finds a match
            if media_id:
                # Set media_id to only the numbers in the match
                media_id = media_id.group(1)
                break

        return media_id


if __name__ == "__main__":  # BuhmB7Ih1J4  # CCeGDPkDWJ4
    # filename = "json/posts/mutli_video_austinjkaufman_post_CfvfiieOjXz.json"
    # filename = "json/posts/single_video_sony_post_Cfhkjtespv6.json"
    filename = "json/posts/single_image_austinjkaufman_post_BuhmB7Ih1J4.json"
    # with open(filename, encoding='utf-8') as file:
    #     post = Post(json.load(file))
    #
    # print(post.short_code)
    # for item in post.likes:
    #     print(item)
    test = PostManager(InstagramScraper())
    test.get_user_posts()
    # import pickle
    #
    # # with open("json/post_test_toy_toky", "rb") as file:
    # #     test = pickle.load(file)
    # with open("json/post_test_toy_toky", "wb") as file:
    #     pickle.dump(test, file)
    #
    # post = test.posts[0]
    #
    # for key, value in post.__dict__.items():
    #     print(f"{key}\t|||\t\t{value}")
    #
    # print()
    # print(post.media[0])
    # with open("json/save_file.html", "w", encoding='utf-8') as file:
    #     file.write(test.session.get("https://www.instagram.com/p/CgHcL2FO2UK/").text)
