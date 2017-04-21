
# average length of comment
sql_avg_length = '''SELECT AVG(length(raw_comment)) as avg_length, forum_id as forum from data_comment group by forum_id;'''

#count of comments per day
sql_comment_count = '''select name, to_char(date_posted, 'day') as dow, count(*) from data_comment join data_forum on data_comment.forum_id = data_forum.id group by name, dow order by name, dow;'''

#count of comments per day order by day of week; 0 is Sunday
sql_comment_count_per_day = '''select name, extract(dow from date_posted) as dow, count(*) from data_comment join data_forum on data_comment.forum_id = data_forum.id group by name, dow order by name, dow;'''

### percentage by day of week
sql_percent_dow = '''select name, extract(dow from date_posted) as dow, count(*), total_count, round(100.0 * count(*) /  total_count,1)  as percentage
                    from data_comment
                    join data_forum
                         on data_comment.forum_id = data_forum.id
                    join
                         (select data_forum.id as tab_id, count(*) as total_count
                              from data_comment
                              join data_forum
                                   on data_comment.forum_id = data_forum.id
                              group by data_forum.id) as total_ct_table
                         on total_ct_table.tab_id = data_comment.forum_id
                    group by name, dow, total_count
                    order by name, dow;'''

#### percentage of comments per hour
sql_percent_hour = '''select name, extract(hour from date_posted) as hour, count(*), total_count, round(100.0 * count(*) /  total_count, 1)  as percentage
                         from data_comment
                         join data_forum
                              on data_comment.forum_id = data_forum.id
                         join
                              (select data_forum.id as tab_id, count(*) as total_count
                                   from data_comment
                                   join data_forum
                                        on data_comment.forum_id = data_forum.id
                                   group by data_forum.id) as total_ct_table
                              on total_ct_table.tab_id = data_comment.forum_id
                         group by name, hour, total_count
                         order by name, hour;'''

### percentage of comments by week
sql_percent_week = '''select name, extract(week from date_posted) as week, count(*), total_count, round(100.0 * count(*) /  total_count, 1)  as percentage
                    from data_comment
                    join data_forum
                         on data_comment.forum_id = data_forum.id
                    join
                         (select data_forum.id as tab_id, count(*) as total_count
                              from data_comment
                              join data_forum
                                   on data_comment.forum_id = data_forum.id
                              group by data_forum.id) as total_ct_table
                         on total_ct_table.tab_id = data_comment.forum_id
                    group by name, week, total_count
                    order by name, week;'''

#first and most recent comment by forum
sql_timespan = '''select name, max(date_posted) as last_comment,  min(date_posted) as first_comment
                    from data_comment
                    join data_forum
                         on data_comment.forum_id = data_forum.id
                    group by name;'''

#number of comments from cross posters
sql_cross_poster = '''with cross_poster as (select api_author_id::integer, count(api_author_id) as num_forums
                         from data_author
                         group by api_author_id
                         having count(api_author_id) > 1)
                    select count(raw_comment)
                        from data_comment
                        where author_id in (select id
                                          from data_author
                           where api_author_id::integer in (select api_author_id from cross_poster));'''

#more information about cross posters
sql_cross_poster_details = '''with cross_poster as (select api_author_id::integer, count(api_author_id) as num_forums
                              from data_author
                              group by api_author_id
                              having count(api_author_id) > 2)
                              select api_author_id, data_forum.name as outlet, count(raw_comment) as comments_count
                              from data_comment
                              join data_forum on data_comment.forum_id = data_forum.id
                              join data_author on data_comment.author_id = data_author.id
                              where author_id in (select id
                                   from data_author
                                   where api_author_id::integer in (select api_author_id from cross_poster))
                              group by api_author_id, outlet
                              order by api_author_id;'''
