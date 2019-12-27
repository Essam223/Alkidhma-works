odoo.define('message_groupchat.chat_manager', function(require) {
    "use strict";
    var chat_manager = require('mail.chat_manager');
    console.log("ddddddddddddddddddddddddd", chat_manager)
    chat_manager.include({
        add_message: function add_message (data,options) {
            console.log("new................................")
        },
    });
//    chat_manager.function.include({
//        add_message: function(data, options) {
//            console.log("old.lllllllll...............................")
//        },
//    });





//function add_message (data, options) {
//    options = options || {};
//    var msg = _.findWhere(messages, { id: data.id });
//    if (!msg) {
//        msg = chat_manager.make_message(data);
//        // Keep the array ordered by id when inserting the new message
//        messages.splice(_.sortedIndex(messages, msg, 'id'), 0, msg);
//        _.each(msg.channel_ids, function (channel_id) {
//            var channel = chat_manager.get_channel(channel_id);
//            if (channel) {
//                // update the channel's last message (displayed in the channel
//                // preview, in mobile)
//                if (!channel.last_message || msg.id > channel.last_message.id) {
//                    channel.last_message = msg;
//                }
//                add_to_cache(msg, []);
//                if (options.domain && options.domain !== []) {
//                    add_to_cache(msg, options.domain);
//                }
//                if (channel.hidden) {
//                    channel.hidden = false;
//                    chat_manager.bus.trigger('new_channel', channel);
//                }
//                console.log(channel.type, msg.is_author, msg.is_system_notification)
//                if (channel.type !== 'static' && !msg.is_author && !msg.is_system_notification) {
//                    console.log("msg......................", channel.is_chat,options.show_notification)
//                    if (options.increment_unread) {
//                        update_channel_unread_counter(channel, channel.unread_counter+1);
//                    }
//                    if (channel.is_chat && options.show_notification) {
//                        if (!client_action_open && !config.device.isMobile) {
//                            // automatically open chat window
//                            chat_manager.bus.trigger('open_chat', channel, { passively: true });
//                        }
//                        var query = {is_displayed: false};
//                        chat_manager.bus.trigger('anyone_listening', channel, query);
//                        notify_incoming_message(msg, query);
//                    }
//                    if (!channel.is_chat && options.show_notification) {
//                        if (!client_action_open && !config.device.isMobile) {
//                            // automatically open chat window
//                            chat_manager.bus.trigger('open_chat', channel, { passively: true });
//                        }
//                        var query = {is_displayed: false};
//                        chat_manager.bus.trigger('anyone_listening', channel, query);
//                        notify_incoming_message(msg, query);
//                    }
//                    if (channel.is_chat && !options.show_notification) {
//                        if (!client_action_open && !config.device.isMobile) {
//                            // automatically open chat window
//                            chat_manager.bus.trigger('open_chat', channel, { passively: true });
//                        }
//                        var query = {is_displayed: false};
//                        chat_manager.bus.trigger('anyone_listening', channel, query);
//                        notify_incoming_message(msg, query);
//                    }
//                }
//            }
//        });
//        if (!options.silent) {
//            chat_manager.bus.trigger('new_message', msg);
//        }
//    } else if (options.domain && options.domain !== []) {
//        add_to_cache(msg, options.domain);
//    }
//    return msg;
//}
});
