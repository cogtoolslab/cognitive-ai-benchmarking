Directory to contain experiment code (e.g., HTML/CSS/JavaScript) for this project.

To run the experiment, run `node app.js --gameport PORT` where PORT is the port number you want to use. If don't want to use the mongoDB backend (we recommend using the mongoDB backend), run `node app.js --gameport PORT --local_store`.
Only one version of `app.js` needs to be run for all experiments.

### Checklist for starting data collection on new online experiment
- Complete your OSF pre-registration worksheet
- Make sure that data is being saved correctly by drafting your analysis notebook
- Write instructions
- Figure out how subject payment is going to work
- Add consent form to appear before instructions

#### Using Amazon Mechanical Turk?
- Configure HIT settings using nosub: https://github.com/longouyang/nosub
- Test task out in MTurk Sandbox

### Using Prolific? 
- `TODO: add instructions here`
