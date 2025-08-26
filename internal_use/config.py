real_fdb_config = dict(
    type="local",
    engine="toc",
    schema="/store_new/mch/msopr/rea-l-ch1/fdb/schema",
    spaces=[
        dict(
            handler="Default",
            roots=[
                {"path": "/store_new/mch/msopr/rea-l-ch1/fdb/spinup"},
            ],
        )
    ],
)
