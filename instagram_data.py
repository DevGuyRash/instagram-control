import json
from sessions import InstagramSession
from datetime import datetime
from bs4 import BeautifulSoup
import re


class InstagramPage:

    def __init__(self, instagram_json):
        self.page = instagram_json


class User:
    """
    Class meant to hold all info related to an instagram user.

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

    def __init__(self, username: str, json_data: dict):  # TODO Create sub-folder
        with open(f"json/{username}.json", 'w', encoding='utf-8') as file:
            json.dump(json_data, file)

        self.username = username

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
               f"Followers: {self.followers} | Following: {self.following}\n" \
               f"Category: {self.category}\n" \
               f"Website: {self.website}\n" \
               f"Bio: {self.bio}"


class Post:
    """
    Class containing all information about an Instagram post.

    Attributes:
        likes_and_views_disabled (bool): Whether the likes and view
            counts are disabled or not.
        comment_likes_enabled (bool): Whether comment likes are enabled
            or not.
        username (str): Username of the account that posted this post.
        media_type (str): Format of the media in the post (different
            numbers meaning photo, video, gif, etc.)
        access_caption (str): The accessibility caption associated with
            the post, if there is one.
        users_tagged (list): List of users tagged in this post.
        pk (str): Unique id associated with the post.
        id (str): Unique id associated with the post.
        url_id (str): Unique url id used to access this post, usually
            found towards the end of the url when you are on the post.
        created (str): Timestamp of when the post was created.
        created_formatted (datetime): `Datetime` object of when the post
            was created.
        comments (str): Total amount of comments on the post.
        likes (str): Total amount of likes on the post.
        caption (Comment): The caption of the post, made by the poster.
    """

    def __init__(self, json_data):
        print(json_data)  # TODO FOR DEBUGGING
        # Create base index path to get the rest of the data from
        base = json_data["items"][0]

        # Perform checks on post to verify data retrieval
        self.likes_and_views_disabled = base.get('like_and_view_counts_disabled')
        self.comment_likes_enabled = base.get('comment_likes_enabled')

        # Basic post info
        self.username = base["user"]["username"]
        self.media_type = base.get('media_type')

        # These keys aren't always present
        self.access_caption = base.get('accessibility_caption')

        usertags = base.get('usertags')
        if usertags:
            self.users_tagged = [username["user"]["username"]
                                 for username in base["usertags"]["in"]]
        else:
            self.users_tagged = []

        # Media ID's unique to this post
        self.pk = base.get('pk')
        self.id = base.get('id')

        # Use the url_id with the user-post link in urls to go to the post.
        self.url_id = base.get('code')

        # Creation time
        self.created = base.get('taken_at')
        self.created_formatted = datetime.fromtimestamp(self.created)

        # Post metrics
        self.comments = base.get("comment_count")
        self.likes = base.get("like_count")

        caption = base.get('caption')

        # Create Comment object from caption to display organized info
        if caption:
            self.caption = Comment(
                username=self.username,
                text=caption.get('text'),
                created=caption.get('created_at_utc')
            )
        else:
            self.caption = ""

        # Save the json file
        with open(f"json/{self.username}_post_{self.pk}.json", 'w', encoding='utf-8') as file:
            json.dump(json_data, file)

    def __str__(self):
        return f"ID: {self.id}\n" \
               f"URL_ID: {self.url_id}\n" \
               f"By: {self.username}\n" \
               f"Caption: {self.caption}\n" \
               f"Total Likes: {self.likes}\n" \
               f"Total Comments: {self.comments}\n" \
               f"Created on: {self.created_formatted}"


class Comment:

    def __init__(self,
                 username: str,
                 text,
                 created: int,
                 likes: int = 0,
                 ):
        self.username = username
        self.text = text
        self.created = created
        self.created_formatted = datetime.fromtimestamp(self.created)
        self.likes = likes

    def __str__(self):
        return f"{self.text}\n" \
               f"-{self.username}, at {self.created_formatted}\n" \
               f"Likes: {self.likes or 'Doesnt apply'}"


class Tag:
    pass


if __name__ == "__main__":
    pass
