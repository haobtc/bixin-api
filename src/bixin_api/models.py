import json


class PlatformUser:
    """
    Data is like:
    {
        "username": "unique-internal-username",
        "verified": True,
        "vendor.BTC.cash": "0",
        "vendor.BTC.hold": "0",
        "vendor.BCC.hold": "0",
        "vendor.ETH.cash": "0",
        "vendor.ETH.hold": "0",
        "vendor.CNY.cash": "0",
        "vendor.BCC.cash": "0",
        "vendor.CNY.hold": "0",
        "target_id": "8c82ca5cf0374185a663cf9bc298f65e",
        "avatar_url": "https://ojjwxmb4j.qnssl.com/upload/2017/09/28/3f8742a776b24e10ab196a5449737c3e.png-thumb",
        "lock": {
            "is_locked": False, "reason": "", "endtime": 0
        },
        "fullname": "the-display-name",
        "id": 125103,
    }
    """

    def __init__(
            self,
            id,
            username,
            verified,
            target_id,
            avatar_url,
            lock,
            fullname,
            openid=None,
            **vendor_assets
    ):
        self.openid = openid
        self.id = id
        self.username = username
        self.verified = verified
        self.target_id = target_id
        self.avatar_url = avatar_url
        self.lock = lock
        self.fullname = fullname
        self.vendor = vendor_assets

    def is_verified(self):
        """
        If a user passed all kinds of identification it will be true, else false.
        """
        return self.verified

    @classmethod
    def from_raw(cls, json_resp):
        return cls(**json_resp)

    def as_dict(self):
        return dict(
            id=self.id,
            username=self.username,
            verified=self.verified,
            target_id=self.target_id,
            avatar_url=self.avatar_url,
            lock=self.lock,
            fullname=self.fullname,
            vendor=self.vendor,
            openid=self.openid,
        )


class BixinVendorUser:
    """
    type VendorUserInfo {
        openid: String
        target_id: String
        username: String
        fullname: String
        avatar_url: String
        verified: Boolean
        is_locked: Boolean
        wallet_balance: JSONString
        vendor_fund_balance: JSONString
        verifiedInfo: userVerifyInfo
    }
    """
    def __init__(
            self,
            openid,
            target_id,
            username,
            fullname,
            avatar_url,
            verified,
            is_locked,
            wallet_balance,
            vendor_fund_balance,
            verifiedInfo,
    ):
        self.openid = openid
        self.target_id = target_id
        self.username = username
        self.fullname = fullname
        self.avatar_url = avatar_url
        self.verified = verified
        self.is_locked = is_locked
        self.wallet_balance = json.loads(wallet_balance) if wallet_balance else {}
        self.vendor_fund_balance = json.loads(vendor_fund_balance) if vendor_fund_balance else {}
        self.verified_info = verifiedInfo
