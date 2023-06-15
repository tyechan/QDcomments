create database dev_qidianbooks;
use dev_qidianbooks;

create 
or replace table tb_comments( 
    id int unsigned not null primary key auto_increment
    , reviewid varchar (30) not null
    , segmentid int not null
    , chapterid varchar (30) not null
    , bookid varchar (30) not null
    , cbid varchar (30) not null
    , ccid varchar (30) not null
    , guid varchar (30) not null
    , userid varchar (30) not null
    , nickname varchar (100) not null
    , content varchar (600) not null
    , status int unsigned not null
    , createtime datetime not null
    , quotereviewid varchar (30)
    , quotecontent varchar (600)
    , quoteguid varchar (30)
    , quoteuserid varchar (30)
    , quotenickname varchar (600)
    , type int unsigned
    , likecount int unsigned not null
    , level int unsigned
    , imagepre varchar (100)
    , imagedetail varchar (100)
    , rootreviewid varchar (30)
    , rootreviewreplycount int unsigned
    , ipaddress varchar (30)
)charset=utf8mb4; 

create
or replace table tb_books(
    id int unsigned not null primary key auto_increment
    , bookid varchar (30) not null
    , filename varchar (255) not null
    , status int unsigned default 0
    , title varchar (30)
    , author varchar (100)
    , description varchar (1000)
    , tags varchar (100)
    , textcount int unsigned
    , createtime datetime
    , updatetime datetime
)charset=utf8mb4;

create 
or replace table tb_chapters( 
    id int unsigned not null primary key auto_increment
    , chapterid varchar (30)
    , bookid varchar (30) not null
    , chapternum int unsigned not null
    , title varchar (100) not null
    , status int unsigned default 0
    , updatetime datetime
)charset=utf8mb4; 

create 
or replace table tb_segments( 
    id int unsigned not null primary key auto_increment
    , segmentid int
    , chapterid varchar (30)
    , bookid varchar (30) not null
    , chapternum int unsigned not null
    , segmentnum int unsigned not null
    , status int unsigned default 0
    , content varchar (1000)
)charset=utf8mb4; 

create 
or replace table tb_users( 
    id int unsigned not null primary key auto_increment
    , token varchar (30) not null
    , username varchar (30) not null
    , permissions int unsigned default 0
    , status int unsigned default 1
    , createtime datetime
)charset=utf8; 

-- alter table tb_comments default character set utf8mb4;
-- alter table tb_books default character set utf8mb4;
-- alter table tb_chapters default character set utf8mb4;
-- alter table tb_segments default character set utf8mb4;

insert into dev_qidianbooks.tb_books(bookid,filename,status,title,author,description,tags,textcount,createtime,updatetime) values 
    ('1025901449','《我的治愈系游戏》（校对版全本）作者：我会修空调.txt','1','我的治愈系游戏','我会修空调','警察同志，如果我说这是一款休闲治愈系游戏，你们信吗？',null,null,null,null);
