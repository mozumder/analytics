prepare log(
    timestamp,      -- 01 Request Time Stamp
    inet,           -- 02 IP Address
    real,           -- 03 Response Time
    smallint,       -- 04 HTTP status code
    varchar(200),   -- 05 request url
    varchar(50),    -- 06 request_content_type Mime Type
    char(1),        -- 07 Method
    bool,           -- 08 AJAX
    varchar(200),   -- 09 referer url
    varchar(200),   -- 10 user_agent,
    integer,        -- 11 request_content_length
    varchar(100),   -- 12 Accept Types
    varchar(50),    -- 13 Accept Language
    varchar(50),    -- 14 Accept Encoding
    varchar(50),    -- 15 response_content_type Mime Type
    integer,        -- 16 response_content_length
    char(1),        -- 17 compress
    varchar(40),    -- 18 session_id
    integer,        -- 19 user_id
    numeric,        -- 20 Latitude
    numeric,        -- 21 Longitude
    char(1),        -- 22 Protocol
    bool,           -- 23 Cached
    timestamp,      -- 24 session_start_time
    bool,           -- 25 preview
    bool,           -- 26 prefetch
    bool            -- 27 bot
    )
as
    with ip as (
        insert into
                analytics_ip
            (
                address,
                bot
            )
        values
            (
                $2,
                $27
            )
        on conflict do nothing
        returning id
    ),
    request_url as (
        insert into
                analytics_url
            (
                name,
                scheme
            )
        select
            $5,
            false
        where
            $5 NOTNULL
        on conflict do nothing
        returning id
    ),
    request_content_type as (
        insert into
                analytics_mime
            (
                mime_type_string
            )
        select
            $6
        where
            $6 NOTNULL
        on conflict do nothing
        returning id
    ),
    referer_url as (
        insert into
                analytics_url
            (
                name,
                scheme
            )
        select
            $9,
            false
        where
            $9 NOTNULL
        on conflict do nothing
        returning id
    ),
    user_agent as (
        insert into
                analytics_useragent
            (
                user_agent_string,
                bot
            )
        select
            $10,
            $27
        where
            $10 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_type as (
        insert into
                analytics_accept
            (
                accept_string
            )
        select
            $12
        where
            $12 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_language as (
        insert into
                analytics_language
            (
                language_string
            )
        select
            $13
        where
            $13 NOTNULL
        on conflict do nothing
        returning id
    ),
    accept_encoding as (
        insert into
                analytics_encoding
            (
                encoding_string
            )
        select
            $14
        where
            $14 NOTNULL
        on conflict do nothing
        returning id
    ),
    response_content_type as (
        insert into
                analytics_mime
            (
                mime_type_string
            )
        select
            $15
        where
            $15 NOTNULL
        on conflict do nothing
        returning id
    ),
    session_log as (
        insert into
                analytics_sessionlog
            (
                session_key,
                start_time,
                user_id,
                bot,
                expire_time
            )
        select
            $18,
            $24,
            $19,
            $27,
            expire_date
        from django_session
        where
            django_session.session_key = $18
        on conflict do nothing
        returning id
    )
    insert into
        analytics_accesslog
    (
        timestamp,
        ip_id,
        response_time,
        status,
        request_url_id,
        request_content_type_id,
        method,
        ajax,
        preview,
        prefetch,
        referer_url_id,
        user_agent_id,
        request_content_length,
        accept_type_id,
        accept_language_id,
        accept_encoding_id,
        response_content_type_id,
        response_content_length,
        compress,
        session_id,
        user_id,
        latitude,
        longitude,
        protocol,
        cached,
        session_log_id,
        log_timestamp
    )
    values
    (
        $1,
        (
            select id from analytics_ip where analytics_ip.address = $2
            union
            select id from ip
        ),
        $3,
        $4,
        (
            select id from analytics_url where analytics_url.name = $5
            union
            select id from request_url
        ),
        (
            select id from analytics_mime where analytics_mime.mime_type_string = $6
            union
            select id from request_content_type
        ),
        $7,
        $8,
        $25,
        $26,
        (
            select id from analytics_url where analytics_url.name = $9
            union
            select id from referer_url
        ),
        (
            select id from analytics_useragent where analytics_useragent.user_agent_string = $10
            union
            select id from user_agent
        ),
        $11,
        (
            select id from analytics_accept where analytics_accept.accept_string = $12
            union
            select id from accept_type
        ),
        (
            select id from analytics_language where analytics_language.language_string = $13
            union
            select id from accept_language
        ),
        (
            select id from analytics_encoding where analytics_encoding.encoding_string = $14
            union
            select id from accept_encoding
        ),
        (
            select id from analytics_mime where analytics_mime.mime_type_string = $15
            union
            select id from response_content_type
        ),
        $16,
        $17,
        $18,
        $19,
        $20,
        $21,
        $22,
        $23,
        (
            select id from analytics_sessionlog where analytics_sessionlog.session_key = $18
            union
            select id from session_log
        ),
        current_timestamp
    )
    returning *
;

