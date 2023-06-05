// Set up sharded collections

sh.enableSharding("films")
db.adminCommand({shardCollection: "films.ratings", key: {film_id: 1}})
db.adminCommand({shardCollection: "films.reviews", key: {review_id: 1}})
db.adminCommand({shardCollection: "films.review_votes", key: {review_id: 1}})
db.adminCommand({shardCollection: "films.bookmarks", key: {film_id: 1}})
