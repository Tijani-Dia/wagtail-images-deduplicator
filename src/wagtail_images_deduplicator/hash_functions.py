import typing

HASH_FUNCTION = typing.Literal[
    "average_hash",
    "phash",
    "dhash",
    "dhash_vertical",
    "whash",
    "colorhash",
]
HASH_FUNCTIONS: typing.Tuple[HASH_FUNCTION] = typing.get_args(HASH_FUNCTION)
