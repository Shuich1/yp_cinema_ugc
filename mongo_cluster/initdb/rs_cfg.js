// Initialize configuration server replica set

rs.initiate({
    _id: "rs_cfg",
    configsvr: true,
    version: 1,
    members: [
        {_id: 0, host: "mongo_cfg_n1:27017"},
        {_id: 1, host: "mongo_cfg_n2:27017"},
        {_id: 2, host: "mongo_cfg_n3:27017"}
    ]
})
