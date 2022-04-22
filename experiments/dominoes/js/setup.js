var DEBUG_MODE = false; //print debug and piloting information to the console
var queryString = window.location.search;
var urlParams = new URLSearchParams(queryString);
var prolificID = urlParams.get("PROLIFIC_PID"); // ID unique to the participant
var studyID = urlParams.get("STUDY_ID"); // ID unique to the study
var sessionID = urlParams.get("SESSION_ID"); // ID unique to the particular submission
var projName = urlParams.get("proj_name");
var expName = urlParams.get("exp_name");
var iterName = urlParams.get("iter_name");
var stimInfo = { proj_name: projName, exp_name: expName, iterName: iterName };

function buildAndRunExperiment(stims) {
  /*
  This function should be modified to fit your specific experiment needs.
  The code you see here is an example for one kind of experiment. 

  The function receives stimuli / experiment configs from your database,
  and should build the appropriate jsPsych timeline. For each trial, make
  sure to specify an onFinish function that saves the trial response.
*/
  var onFinish = function (data) {
    // let's add gameID and relevant database fields
    data.gameID = gameid;
    data.dbname = dbname;
    data.colname = colname;
    data.iterationName = iterName;
    socket.emit("currentData", data);
    if (DEBUG_MODE) {
      console.log(
        "DB:" +
          projName +
          "\nCollection:" +
          expName +
          "\nemitting data: " +
          data
      );
    }
  };

  var trials = constructTrialsForExperiment(data);
  jsPsych.init({
    timeline: trials,
    default_iti: 1000,
    show_progress_bar: true,
  });
}

function launchExperiment() {
  socket.emit("getStims", stimInfo, buildAndRunExperiment(stims));
}

// at end of each trial save data locally and send data to server
var stim_on_finish = function (data) {
  // let's add gameID and relevant database fields
  data.gameID = gameid;
  data.dbname = dbname;
  data.colname = colname;
  data.iterationName = itname;
  data.stims_not_preloaded = /^((?!chrome|android).)*safari/i.test(
    navigator.userAgent
  ); //HACK turned off preloading stimuli for Safari in jspsych-video-button-response.js
  jsPsych.data.addProperties(jsPsych.currentTrial()); //let's make sure to send ALL the data //TODO: maybe selectively send data to db
  // lets also add correctness info to data
  data.correct = data.target_hit_zone_label == (data.response == "YES");
  if (data.correct) {
    correct += 1;
  }
  total += 1;
  if (DEBUG_MODE) {
    if (data.correct) {
      console.log(
        "Correct, got ",
        _.round((correct / total) * 100, 2),
        "% correct"
      );
    } else {
      console.log(
        "Wrong, got ",
        _.round((correct / total) * 100, 2),
        "% correct"
      );
    }
  }
  last_correct = data.correct; //store the last correct for familiarization trials
  last_yes = data.response == "YES"; //store if the last reponse is yes
  socket.emit("currentData", data);
  if (DEBUG_MODE) {
    console.log("emitting data", data);
  }
};

var stim_log = function (data) {
  if (DEBUG_MODE) {
    console.log(
      "This is " + data.stim_ID + " with label " + data.target_hit_zone_label
    );
  }
};
