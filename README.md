# Cognitive-AI Benchmarking Project Template: Human Behavioral Experiments
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This is a fully worked example based on the [Physion project](https://github.com/cogtoolslab/physics-benchmarking-neurips2021).

It contains several subdirectories that will contain standard components of the human behavioral experimental infrastructure that will support a variety of Cognitive-AI Benchmarking projects.

- `analysis` (aka `notebooks`): This directory will typically contain jupyter/Rmd notebooks for exploratory code development and data analysis.
- `experiments`: If this is a project that will involve collecting human behavioral data, this is where you want to put your experimental code. If this is a project that will involve evaluation of a computational model's behavior on a task, this is also where you want to put the task code.
- `results`: This directory is meant to contain "intermediate" results of your computational/behavioral experiments. It should minimally contain two subdirectories: `csv` and `plots`. So `/results/csv/` is the path to use when saving out `csv` files containing tidy dataframes. And `/results/plots/` is the path to use when saving out `.pdf`/`.png` plots, a small number of which may be then polished and formatted for figures in a publication. *Important: Before pushing any csv files containing human behavioral data to a public code repository, triple check that these data files are properly anonymized. This means no bare AMT Worker ID's.* It is generally recommended that "raw" behavioral data be stored in a database rather than as part of this repo.
- `stimuli`: This directory is meant to contain any download/preprocessing scripts for data that are _inputs_ to this project. For many projects, these will be images. This is also where you want to place any scripts that will upload your data to our `stimuli`  MongoDB database and any image data to Amazon S3 (so that it has a semi-permanent URL you can use to insert into your web experiment.)



## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://ac.felixbinder.net"><img src="https://avatars.githubusercontent.com/u/24477285?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Felix Binder</b></sub></a><br /><a href="#maintenance-felixbinder" title="Maintenance">🚧</a> <a href="#mentoring-felixbinder" title="Mentoring">🧑‍🏫</a></td>
    <td align="center"><a href="http://yonifriedman.com"><img src="https://avatars.githubusercontent.com/u/26826815?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yoni Friedman</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=yifr" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/yamins81"><img src="https://avatars.githubusercontent.com/u/231307?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Dan Yamins</b></sub></a><br /><a href="#eventOrganizing-yamins81" title="Event Organizing">📋</a></td>
    <td align="center"><a href="https://github.com/thomaspocon"><img src="https://avatars.githubusercontent.com/u/5657644?v=4?s=100" width="100px;" alt=""/><br /><sub><b>thomaspocon</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=thomaspocon" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/HaoliangWang"><img src="https://avatars.githubusercontent.com/u/26497509?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Haoliang Wang</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=HaoliangWang" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/justintheyang"><img src="https://avatars.githubusercontent.com/u/51468707?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Justin Yang</b></sub></a><br /><a href="https://github.com/cogtoolslab/cognitive-ai-benchmarking/commits?author=justintheyang" title="Code">💻</a></td>
    <td align="center"><a href="http://rxdhawkins.com"><img src="https://avatars.githubusercontent.com/u/5262024?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Robert Hawkins</b></sub></a><br /><a href="#tool-hawkrobe" title="Tools">🔧</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!