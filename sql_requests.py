queries = {
    'get_id_of_artist': "SELECT `id_artist` FROM `artist` WHERE `stage_name` = %s",
    'get_id_of_place': "SELECT `id_place` FROM `place` WHERE `name` = %s",
    'add_venue_to_db': "INSERT INTO `concert` (`id_artist`, `id_place`, `datetime`) VALUES (%s, %s, %s)",
    'get_artists_venues': "SELECT artist.`stage_name`, place.`name`, place.`city`, place.`country`, place.`address`, concert.`datetime` "
                          "FROM (`concert` JOIN `place` ON concert.`id_place` = place.`id_place`) "
                          "JOIN `artist` ON concert.`id_artist` = artist.`id_artist` "
                          "WHERE concert.`id_artist` = %s ORDER BY concert.`datetime`",
    'check_existence_of_city': "SELECT COUNT(*) FROM place WHERE place.`city` = %s",
    'get_venues_in_city': "SELECT artist.`stage_name`, place.`name`, place.`city`, place.`country`, place.`address`, concert.`datetime` "
                          "FROM (`concert` JOIN `place` ON concert.`id_place` = place.`id_place`) "
                          "JOIN `artist` ON concert.`id_artist` = artist.`id_artist` "
                          "WHERE place.`city` = %s ORDER BY concert.`datetime`"
}
