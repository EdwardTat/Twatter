// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        sbar: '',
        users_list: [],
        pbar: '',
        posts_list: [],
        rbar: ''
    };

    app.annotate_meows = (a) => {
        let k = 0;
        a.map((e) => {
            e.uname = e.username;
            e.urn = e.rn;
            e.utime = Sugar.Date(e.timestamp).relative();
            e.upost = e.post;
            e.ureplyID = e.replyID;
            e.urbar = false;
        });
        return a;
    }


    app.annotate = (a) => {
        let k = 0;
        a.map((e) => {
            e.uname = e.following;
            e.ustatus = e.status;
        });
        return a;
    }



    app.get_user_posts = function (u_idx) {
        console.log("uidx = " + u_idx + "\n");
        let id = u_idx;
        axios.get(get_user_p_url, { params: { id: id } }).then(function (r) {
            app.vue.posts_list = app.annotate_meows(r.data.posts);
            app.enumerate(app.vue.posts_list);
            app.vue.rbar = ''
        });
    };


    app.get_meow_replies = function (u_idx) {
        console.log("u = " + u_idx + "\n");
        for (let i = 0; i < app.vue.posts_list.length; i++) {
            app.vue.posts_list[i].urbar = false;
        }
        app.vue.posts_list[u_idx].urbar = true;
        let id = app.vue.posts_list[u_idx].id;
        console.log("id = " + id + "\n");
        console.log("typeof(posts_list) = " + typeof (app.vue.posts_list) + "\n")
        axios.get(get_replies_url, { params: { id: id } }).then(function (r) {
            tposts = app.annotate_meows(r.data.posts);
            console.log(tposts.length)
            for (let i = tposts.length - 1; i >= 0; i--)
                app.vue.posts_list.splice(u_idx + 1, 0, tposts[i]);
            //app.vue.posts_list = app.annotate_meows(app.vue.posts_list);
            app.enumerate(app.vue.posts_list);
        });
    };

    app.get_retweets_button = function (post) {
        temp = "RT " + post.uname + ": " + post.post;
        axios.get(post_new_meow_url, { params: { q: temp } }).then(function (r) {
            app.vue.pbar = "";

        });
    };


    app.view_feed_posts = function () {
        console.log("postlist aquired\n\n");
        axios.get(get_feed_meows_url, { params: {} }).then(function (r) {
            app.vue.posts_list = app.annotate_meows(r.data.posts);
            console.log("feed aquired\n\n");
            app.enumerate(app.vue.posts_list);
        });
    };

    app.your_posts = function () {
        console.log("your called\n\n");
        axios.get(get_your_meows_url, { params: {} }).then(function (r) {
            app.vue.posts_list = app.annotate_meows(r.data.posts);
            console.log("your aquired\n\n");
            app.enumerate(app.vue.posts_list);
        });
    };


    app.view_recent_posts = function () {
        console.log("postlist aquired\n\n");
        axios.get(get_recent_meows_url, { params: {} }).then(function (r) {
            app.vue.posts_list = app.annotate_meows(r.data.posts);
            app.enumerate(app.vue.posts_list);
            console.log("postlist aquired\n\n");
        });
    };

    app.set_follow = function (u_idx) {
        console.log(u_idx);
        let id = (app.vue.users_list[u_idx]).following;
        console.log("\n\n" + id);
        axios.get(follow_url, { params: { id: id } }).then(function (response) {
            //          location.reload();
            app.do_search();
        });

    };

    app.bpublish = function () {
        console.log("bpublish called\n");
        axios.get(post_new_meow_url, { params: { q: app.vue.pbar } }).then(function (r) {
            app.vue.pbar = "";

        });
    };

    app.reply_to_post = function (p_idx) {
        let id = (app.vue.posts_list[p_idx].id);
        axios.get(post_new_reply_url, { params: { x: app.vue.rbar, id: id } }).then(function (r) {

        });
        rbar = "";
    }

    app.clear_search = function () {
        app.vue.sbar = "";
        app.vue.do_search();
    };



    app.do_search = function () {
        axios.get(get_users_url, { params: { q: app.vue.sbar } })
            .then(function (r) {
                app.vue.users_list = app.annotate(r.data.users);
                app.vue.users_list = app.vue.users_list.concat(app.annotate(r.data.users2));
                app.enumerate(app.vue.users_list);
            })
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };

    // This contains all the methods.

    app.methods = {
        // Complete as you see fit.
        enumerate: app.enumerate,
        annotate: app.annotate,
        annotate_meows: app.annotate_meows,
        view_recent_posts: app.view_recent_posts,
        do_search: app.do_search,
        clear_search: app.clear_search,
        set_follow: app.set_follow,
        view_your_feed_posts: app.view_your_feed_posts,
        bpublish: app.bpublish,
        view_feed_posts: app.view_feed_posts,
        your_posts: app.your_posts,
        get_user_posts: app.get_user_posts,
        get_retweets_button: app.get_retweets_button,
        get_meow_replies: app.get_meow_replies,
        reply_to_post: app.reply_to_post,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        app.vue.do_search();
        console.log("do search called\n");
        app.vue.view_recent_posts();
        console.log("view posts did not fail\n")

    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
