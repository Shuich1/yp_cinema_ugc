// Initialize sharded cluster

sh.addShard("rs_s1/mongo_s1_n1:27017")
sh.addShard("rs_s1/mongo_s1_n2:27017")
sh.addShard("rs_s1/mongo_s1_n3:27017")
sh.addShard("rs_s2/mongo_s2_n1:27017")
sh.addShard("rs_s2/mongo_s2_n2:27017")
sh.addShard("rs_s2/mongo_s2_n3:27017")
