"use client";

import React, { useEffect, useState } from "react";
import { fetchActivities, Activity } from "../lib/api";
import { MessageSquare, Clock, User } from "lucide-react";

export default function ActivityFeed() {
    const [activities, setActivities] = useState<Activity[]>([]);
    const [loading, setLoading] = useState(true);

    const loadActivities = async () => {
        try {
            const data = await fetchActivities(10);
            setActivities(data);
        } catch (err) {
            console.error("Failed to load activities", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadActivities();
        const interval = setInterval(loadActivities, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading && activities.length === 0) {
        return (
            <div className="p-4 space-y-4">
                {[1, 2, 3].map(i => (
                    <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse" />
                ))}
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full overflow-hidden">
            <div className="flex items-center gap-2 mb-4 px-4">
                <MessageSquare className="w-4 h-4 text-status-new" />
                <h3 className="text-xs font-bold uppercase tracking-widest text-white">Agent Activities</h3>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 px-4 pb-4 scrollbar-thin">
                {activities.map((activity) => (
                    <div key={activity.id} className="bg-white/[0.03] border border-white/5 rounded-xl p-3 text-[11px] hover:bg-white/5 transition-colors">
                        <div className="flex items-center justify-between mb-1.5">
                            <div className="flex items-center gap-1.5">
                                <div className="w-4 h-4 rounded-full bg-status-new/20 flex items-center justify-center">
                                    <User className="w-2.5 h-2.5 text-status-new" />
                                </div>
                                <span className="font-bold text-white">{activity.agent}</span>
                            </div>
                            <div className="flex items-center gap-1 text-[9px] text-foreground-muted">
                                <Clock className="w-2.5 h-2.5" />
                                <span>{new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                        </div>
                        <p className="text-foreground-muted leading-relaxed italic">
                            "{activity.message}"
                        </p>
                    </div>
                ))}
                {activities.length === 0 && (
                    <div className="text-center py-10">
                        <p className="text-[10px] text-foreground-muted italic">No activity recorded yet.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
