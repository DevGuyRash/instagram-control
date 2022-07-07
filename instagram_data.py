import json
from sessions import InstagramSession
from datetime import datetime
from bs4 import BeautifulSoup
import re


class InstagramPage:

    def __init__(self, instagram_json):
        self.page = instagram_json


class User:

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

    def __init__(self, json_data):
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
            self.users_tagged = ""

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
