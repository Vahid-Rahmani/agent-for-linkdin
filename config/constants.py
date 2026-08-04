class LinkedInUrls:
    HOME = "https://www.linkedin.com/feed/"
    LOGIN = "https://www.linkedin.com/login"
    PROFILE = "https://www.linkedin.com/in/"
    MESSAGES = "https://www.linkedin.com/messaging/"
    NOTIFICATIONS = "https://www.linkedin.com/notifications/"


class LinkedInSelectors:
    LOGIN_USERNAME = 'input#username'
    LOGIN_PASSWORD = 'input#password'
    LOGIN_SUBMIT = 'button[type="submit"]'
    POST_BUTTON = 'button.share-box-feed-entry__trigger'
    POST_EDITOR = 'div.share-creation-state__editor'
    POST_SUBMIT = 'button.share-actions__primary-action'
    POST_VISIBILITY = 'button.artdeco-dropdown__trigger'
    COMMENT_INPUT = 'textarea.comments-comment-box__input'
    COMMENT_SUBMIT = 'button.comments-comment-box__submit-button'
    MESSAGE_INPUT = 'textarea.msg-form__contenteditable'
    MESSAGE_SUBMIT = 'button.msg-form__send-button'
    LIKE_BUTTON = 'button.react-button__trigger'
    POST_CONTENT = 'div.feed-shared-update-v2'
    COMMENT_CONTENT = 'span.comments-comment-item__main-content'
    AUTHOR_NAME = 'span.feed-shared-actor__name'
    POST_TIME = 'span.feed-shared-actor__sub-description'
    NOTIFICATION_ITEM = 'li notifications-inbox__item'
    PROFILE_VIEWS = 'span.profile-views__count'
    SEARCH_APPEARANCES = 'span.search-appearances__count'
    EDIT_POST_BUTTON = 'button.feed-shared-update-v2__edit-btn'
    EDIT_POST_EDITOR = 'div.share-creation-state__editor'
