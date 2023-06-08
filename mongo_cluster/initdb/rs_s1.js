// Initialize shard 1 replica set

rs.initiate({
    _id: "rs_s1",
    version: 1,
    members: [
        {_id: 0, host : "mongo_s1_n1:27017"},
        {_id: 1, host : "mongo_s1_n2:27017"},
        {_id: 2, host : "mongo_s1_n3:27017"},
    ],
})
