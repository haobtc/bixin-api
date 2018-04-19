

def mk_config(
        vendor_name,
        address,
        secret,
        aes_key,
        bot_access_token,
        target_id=None,
):
    return dict(
        name=vendor_name,
        address=address,
        secret=secret,
        aes_key=aes_key,
        bot_access_token=bot_access_token,
        target_id=target_id,
    )
