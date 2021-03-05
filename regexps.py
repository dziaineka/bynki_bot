re_float = r"""
    [+-]?\ *      # first, match an optional sign *and space*
        (             # then match integers or f.p. mantissas:
            \d+       # start out with a ...
            (
                \.\d* # mantissa of the form a.b or a.
            )?        # ? takes care of integers of the form a
            |\.\d+     # mantissa of the form .b
        )
        ([eE][+-]?\d+)?  # finally, optionally match an exponent
    """

re_parse = r"""
    (
        (?:[a-zA-Zа-яА-Я₴$€₽]+)?
        (?:(?:\d+)?(?:\.\d+)?)
        (?:[a-zA-Zа-яА-Я₴$€₽]+)
    ?)
    ([\+\-\*\\])?
"""
