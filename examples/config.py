real_fdb_config = dict(
    type="local",
    engine="toc",
    schema="/scratch/mch/cosuna/rea-l-ch1/schema",
    spaces=[
        dict(
            handler="Default",
            roots=[
                {"path": "/scratch/mch/cosuna/rea-l-ch1_testdata"},
            ],
        )
    ],
)
