// Initialize shard 2 replica set

rs.initiate({
    _id: "rs_s2",
    version: 1,
    members: [
        {_id: 0, host : "mongo_s2_n1:27017"},
        {_id: 1, host : "mongo_s2_n2:27017"},
        {_id: 2, host : "mongo_s2_n3:27017"},
    ],
})
