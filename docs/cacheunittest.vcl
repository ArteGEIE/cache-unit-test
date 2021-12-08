acl dev {
    # ACL we'll use later to allow purges
    "localhost";
    "127.0.0.1";
    "::1";
}

sub vcl_recv  {

	# To avoid any hack based on these headers
	unset req.http.x-cache;
    unset req.http.X-Back;

    if (req.url ~ "^/static/") {
        set req.http.X-Back = "STATIC";
    } else {
        set req.http.X-Back = "WORDPRESS";
    }

    if (req.method == "PURGE") {
        if (!client.ip ~ dev) {
            return(synth(405,"Not allowed."));
        }
        return (purge);
    }
}

sub vcl_hit {
	set req.http.x-cache = "HIT";
	if (obj.ttl <= 0 and obj.grace > 0s) {
		set req.http.x-cache = "HIT_GRACED";
	}
}

sub vcl_miss {
	set req.http.x-cache = "MISS";
}

sub vcl_pass {
	set req.http.x-cache = "PASS";
}

sub vcl_pipe {
	set req.http.x-cache = "PIPE";
}

sub vcl_synth {
    if (!client.ip ~ dev) {
        set resp.http.X-Back = "VARNISH";
        set resp.http.x-cache = "SYNTH";
    }
}

sub vcl_deliver {
    if (!client.ip ~ dev) {
        if (obj.hits > 0) {
            set resp.http.X-NumberOfHits = obj.hits;
        }
        set resp.http.X-Varnish-Server = server.identity;
        set resp.http.X-Back = req.http.X-Back;
        set resp.http.X-Cache = req.http.X-Cache;
    }
}