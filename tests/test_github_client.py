from unittest.mock import MagicMock, patch

from github_client import REVIEW_MARKER, post_review_comment


@patch("github_client.get_repository")
def test_post_review_comment_creates_comment_when_missing(get_repository):
    pr = MagicMock()
    pr.get_issue_comments.return_value = []
    get_repository.return_value.get_pull.return_value = pr

    post_review_comment(7, "Review body")

    pr.create_issue_comment.assert_called_once_with(f"{REVIEW_MARKER}\nReview body")


@patch("github_client.get_repository")
def test_post_review_comment_updates_existing_agent_comment(get_repository):
    comment = MagicMock()
    comment.body = f"{REVIEW_MARKER}\nOld review"
    pr = MagicMock()
    pr.get_issue_comments.return_value = [comment]
    get_repository.return_value.get_pull.return_value = pr

    post_review_comment(7, "New review")

    comment.edit.assert_called_once_with(f"{REVIEW_MARKER}\nNew review")
    pr.create_issue_comment.assert_not_called()
