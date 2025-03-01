from datetime import timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..main import app
from ..models.auction_model import Auction, State
from ..routers.auctions import finish_auction, process_finished_auctions
from .test_helpers import (
    create_mock_auction,
    create_mock_bid,
    create_mock_product,
    create_mock_user,
)

client = TestClient(app)


class TestFinishAuctionTask:
    mock_owner = create_mock_user(1)
    mock_buyer = create_mock_user(2)
    mock_product = create_mock_product(1, mock_owner.id)
    mock_auction = create_mock_auction(1, mock_product)
    mock_bid = create_mock_bid(1, mock_auction.id, mock_buyer.id)

    def test_finish_auction(self):
        with (
            patch.object(
                Auction,
                "get_highest_bid",
                return_value=self.mock_bid,
            ),
            patch(
                "app.routers.auctions.UserPublic.model_validate",
                side_effect=[self.mock_owner, self.mock_buyer],
            ),
            patch(
                "app.routers.auctions.send_auction_email",
                new_callable=AsyncMock,
            ) as mock_send_email,
        ):
            mock_session = MagicMock(spec=Session)
            result = finish_auction(self.mock_auction, mock_session)

            # 🧪 Check auction parameters
            assert result.state == State.finished
            assert result.buyer_id == 2
            assert result.sold_price == Decimal("100")
            assert result.product.sold is True

            # 🧪 Check session calling
            mock_session.add.assert_called_once_with(self.mock_auction)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(self.mock_auction)

            # 🧪 Check email sending
            mock_send_email.assert_any_await(
                self.mock_auction, self.mock_owner
            )
            mock_send_email.assert_any_await(
                self.mock_auction, self.mock_buyer
            )
            assert mock_send_email.await_count == 2

    def test_process_finished_auctions(self):
        mock_auctions = []
        for i in range(5):
            mock_auction = create_mock_auction(auction_id=i)
            mock_auctions.append(mock_auction)

        # Modify auctions; Finished: [0, 3, 4]; Unfinished: [1, 2]
        mock_auctions[1].end_time = None
        mock_auctions[2].end_time += timedelta(days=1)
        mock_auctions[3].end_time += timedelta(days=1)
        mock_auctions[3].instant_buy = True

        with (
            patch(
                "app.routers.auctions.db.read_objects",
                return_value=mock_auctions,
            ),
            patch(
                "app.routers.auctions.finish_auction",
                return_value=None,
            ),
            patch(
                "app.routers.auctions.utils.pretty_print",
                return_value=None,
            ),
        ):
            mock_session = MagicMock(spec=Session)
            result = process_finished_auctions(mock_session)

            # 🧪 Check finished auctions
            assert result == [
                mock_auctions[0].id,
                mock_auctions[3].id,
                mock_auctions[4].id,
            ], "0, 3, 4 are the only finished auctions!"

    def test_error_message_for_no_end_time(self):
        mock_auction = self.mock_auction
        mock_auction.end_time = None

        with (
            patch(
                "app.routers.auctions.db.read_objects",
                return_value=[mock_auction],
            ),
            patch(
                "app.routers.auctions.finish_auction",
                return_value=None,
            ),
            patch(
                "app.routers.auctions.utils.pretty_print"
            ) as mock_pretty_print,
        ):
            mock_session = MagicMock(spec=Session)
            process_finished_auctions(mock_session)

            # 🧪 Check message if auction has no end_time
            mock_pretty_print.assert_called_with(
                "....",
                f"Auction with id {mock_auction.id} has no end_time, resetting state back to setup",
            )

            # 🧪 Check that auction.state is set back to "setup" when no end_time
            assert mock_auction.state == State.setup
