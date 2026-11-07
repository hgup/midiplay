import QtQuick
import QtQuick.Controls
import MuseScore
import FileIO

MuseScore {
    id: pluginRoot
    version: "1.5"
    title: "Midiplay Sync"
    description: "Syncs tempo and meter to midiplay"
    menuPath: "Plugins.Midiplay Sync"
    pluginType: "dialog"
    width: 280
    height: 140

    property int lastBpm: -1
    property int lastNum: -1
    property int lastDen: -1
    property string lastTitle: ""

    FileIO {
        id: stateFile
        source: stateFile.homePath() + "/Documents/MuseScore4/Plugins/musescore_state.json"
        onError: function(msg) { console.log("MidiplaySync FileIO Error: " + msg); }
    }

    function extractTimeSig(m) {
        if (!m) return null;
        try {
            // 1. Try timesigActual fraction (Measure property)
            if (m.timesigActual && m.timesigActual.numerator && m.timesigActual.denominator) {
                return { num: m.timesigActual.numerator, den: m.timesigActual.denominator };
            }
            // 2. Try timesigNominal fraction (Measure property)
            if (m.timesigNominal && m.timesigNominal.numerator && m.timesigNominal.denominator) {
                return { num: m.timesigNominal.numerator, den: m.timesigNominal.denominator };
            }
            // 3. Try m.timesig
            if (m.timesig) {
                if (m.timesig.numerator && m.timesig.denominator) {
                    return { num: m.timesig.numerator, den: m.timesig.denominator };
                }
                if (m.timesig.sigN && m.timesig.sigD) {
                    return { num: m.timesig.sigN, den: m.timesig.sigD };
                }
            }
            // 4. Try segments inside measure
            if (m.firstSegment) {
                for (var seg = m.firstSegment; seg; seg = seg.next) {
                    for (var st = 0; st < (curScore.nstaves || 4); st++) {
                        var el = seg.elementAt(st);
                        if (el) {
                            if (el.sigN && el.sigD) {
                                return { num: el.sigN, den: el.sigD };
                            }
                            if (el.timesig && el.timesig.numerator && el.timesig.denominator) {
                                return { num: el.timesig.numerator, den: el.timesig.denominator };
                            }
                        }
                    }
                }
            }
        } catch(err) {
            console.log("extractTimeSig error: " + err);
        }
        return null;
    }

    function syncState(force) {
        if (!curScore) {
            return "No score open";
        }
        try {
            var cursor = curScore.newCursor();
            var ts = null;
            var bpm = -1;

            // 1. Try Cursor.SELECTION_START (1)
            try {
                cursor.rewind(1); // Cursor.SELECTION_START
                if (cursor.measure) {
                    var selTs = extractTimeSig(cursor.measure);
                    if (selTs) {
                        ts = selTs;
                        if (cursor.tempo > 0) {
                            bpm = cursor.tempo < 20 ? Math.round(cursor.tempo * 60) : Math.round(cursor.tempo);
                        }
                    }
                }
            } catch(e1) {
                console.log("MidiplaySync selection rewind exception: " + e1);
            }

            // 2. Only on initial launch if nothing selected yet, read score start as initial baseline
            if (!ts && lastBpm === -1) {
                try {
                    cursor.rewind(0); // Cursor.SCORE_START
                    if (cursor.measure) {
                        ts = extractTimeSig(cursor.measure);
                    }
                    if (cursor.tempo > 0) {
                        bpm = cursor.tempo < 20 ? Math.round(cursor.tempo * 60) : Math.round(cursor.tempo);
                    } else if (curScore.tempo > 0) {
                        bpm = curScore.tempo < 20 ? Math.round(curScore.tempo * 60) : Math.round(curScore.tempo);
                    }
                } catch(e0) {
                    console.log("MidiplaySync score_start rewind exception: " + e0);
                }
            }

            // 3. If no measure is currently selected and we already have a synced state:
            // KEEP THE LAST SYNCED VALUES! Do not revert to SCORE_START.
            if (!ts) {
                if (lastBpm > 0 && lastNum > 0 && lastDen > 0) {
                    return "Synced: " + lastBpm + " BPM, " + lastNum + "/" + lastDen;
                }
                return "Select a measure in MuseScore";
            }

            var num = ts.num;
            var den = ts.den;
            if (bpm <= 0) {
                bpm = lastBpm > 0 ? lastBpm : (curScore.tempo > 0 ? Math.round(curScore.tempo < 20 ? curScore.tempo * 60 : curScore.tempo) : 120);
            }
            var title = curScore.title || "Untitled score";

            // Dirty check: only write if values changed or forced
            if (!force && bpm === lastBpm && num === lastNum && den === lastDen && title === lastTitle) {
                return "Synced: " + bpm + " BPM, " + num + "/" + den;
            }

            lastBpm = bpm;
            lastNum = num;
            lastDen = den;
            lastTitle = title;

            var payload = JSON.stringify({
                "bpm": bpm,
                "time_sig_num": num,
                "time_sig_den": den,
                "title": title,
                "pos_source": "selection",
                "timestamp": new Date().getTime()
            });

            stateFile.write(payload);
            return "Synced: " + bpm + " BPM, " + num + "/" + den;
        } catch(e) {
            return "Error: " + e;
        }
    }

    Timer {
        id: pollTimer
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            statusText.text = syncState(false);
        }
    }

    Component.onCompleted: {
        statusText.text = syncState(true);
    }

    Rectangle {
        anchors.fill: parent
        color: "#0f172a"

        Column {
            anchors.centerIn: parent
            spacing: 8

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Midiplay Companion Sync"
                color: "#38bdf8"
                font.bold: true
                font.pixelSize: 13
            }

            Text {
                id: statusText
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Syncing..."
                color: "#94a3b8"
                font.pixelSize: 12
            }

            Button {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Sync Now"
                onClicked: {
                    statusText.text = syncState(true);
                }
            }
        }
    }
}
