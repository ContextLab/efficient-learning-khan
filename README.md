# efficient-learning-khan

'''insert experiment/package description'''

## required components

To run the efficient-learning-khan experiment on the Amazon Mechanical Turk platform, you'll need the following software and accounts:

* Docker (v3+):
  https://docs.docker.com/install/
  (required for local use as well)
* PsiTurk account (free):
  https://psiturk.org
* Amazon Web Services account (paid):
  https://aws.amazon.com/console/
  (create a user account and give this user permissions to RDS and MTurk to generate keys)
* Amazon MTurk Sandbox account (free):
  https://requestersandbox.mturk.com/developer
  (create a user account and link to AWS account)
  (for testing prior to going live)
* Amazon MTurk account (see pricing at https://requester.mturk.com/pricing):
  https://requester.mturk.com/developer
  (create a user account and link to AWS account)
* Static public IP address (free):
  (if you are running this experiment through a university, you may need to contact your IT department to acquire this)
* A computer capable of running multiple copies of the experiment simultaneously
* All other requirements are installed when building the docker container. These include:
 * MySQL, v5.7 (https://www.mysql.com/)
 * Adminer (https://www.adminer.org/en/)
 * NGNIX (https://www.nginx.com/)
 * PsiTurk (http://psiturk.org/)
 * JsPsych (https://www.jspsych.org/)


## Installation and Quick Start (for local testing & data collection)

1. Clone the repository `git clone https://github.com/ContextLab/efficient-learning-khan.git`
2. Navigate to the efficient-learning-khan folder in the terminal
    **NOTE**: If you want to change the name, username or password for the MySQL database in which your data will be stored, do so in `docker-compse.yml` before building the docker image.
3. Enter `docker-compose up -d` to build the docker image
4. Attach this image via `docker attach efficient-learning-khan_psiturk_1`
5. This will open a bash shell from within the docker image. From here, enter the command `psiturk` to launch the server followed by `server on`. To debug, enter `debug` and paste the link into the browser.
6. Make sure to update the consent form (`exp/static/templates/consent.html`), lab/university images(`exp/static/favicon.ico`,`exp/static/files/lablogo.png`,`exp/static/files/university.png`) and tasks (`exp/static/js`) as needed for your experiment.
7. Read the section on "Testing or Collecting Data Locally", below, to make sure your configuration is correctly set for local use.


## Experiment Walkthrough

  '''insert experiment walkthrough here'''


## Configuring to Test or Collect Data Locally

Once you've cloned the repo (`git clone https://github.com/ContextLab/efficient-learning-khan.git`) and successfully built the docker container (`docker-compose up -d`), you can begin testing locally.  Make sure the IP address is set to the local host (127.0.0.1) in the following locations:
* `adserver_revproxy_host` in `exp/config.txt`
* `serverporturl` in `exp/static/js/config.js`
You'll also want to check `exp/onfig.txt` to ensure the following:
* Your experiment title, keywords, and experimenter contact are correct
* You've chosen and set a `table_name`
* `debug` is set to `true`
* `launch_in_sandbox_mode` is set to `true`


## Configuring to Test or Collect Data Online via MTurk

Once you've tested the experiment locally and acquired all the components under "required components," you'll need to modify the following:
* Update the following locations to your static public IP address:
 * `adserver_revproxy_host` in `exp/config.txt`
 * `serverporturl` in `exp/static/js/config.js`
* Update the following in `exp/config.txt`:
 * Add any browsers with which your experiment is incompatible to `browser_exclude_rule`
 * Set `aws_access_key_id` and `aws_secret_access_key` to match your AWS access key information
 * Set `psiturk_access_key_id` and `psiturk_secret_access_key` to match your PsiTurk access key information
 * **If you are testing online in Sandbox mode**
  * Set `allow_repeats` to `true`
  * Set `launch_in_sandbox_mode` to `true`
  * Set `debug` to `true`
 * **If you are collecting live data online**
  * Set `allow_repeats` to `false` (so MTurk workers cannot participate in the study multiple times)
  * Set `launch_in_sandbox_mode` to `false`
  * Set `debug` to `false`
* Update the following in `.psiturkconfig`:
 * Set `aws_access_key_id` and `aws_secret_access_key` to match your AWS access key information
 * Set `psiturk_access_key_id` and `psiturk_secret_access_key` to match your PsiTurk access key information
* Add the following to `.gitignore`:
 * `exp/config.txt` (contains your Psiturk and AWS access keys)
 * `.psiturkconfig` (contains your Psiturk and AWS access keys)
 * `docker-compse.yml` (contains your MySQL username and password)
 * `data/*` (contains your MySQL database with experiment data)


## Posting, approving, and removing HITs

After checking the above, ensure that all four of the experiments associated docker images (`efficient-learning-khan_psiturk_1`, `efficient-learning-khan_db_1`, `efficient-learning-khan_adminer_1`, and `efficient-learning-khan_nginx_1`) are running with `docker ps`. Use `docker start` followed by the image name to start any that do not appear.
Launch the PsiTurk container with `docker attach efficient-learning-khan_psiturk_1`. Then, from within the container shell, type `psiturk` to launch PsiTurk.
First, check your AWS account balance with `amt_balance`. If you are in Sandbox mode, this should return a placeholder of $10000. If you are live, this will show your balance.  You can then turn the server on (`server on`) and create hits with `hit create` followed by the number of participants you'd like to collect (or number of test runs you'd like to do if you're in Sandbox mode), the payment amount, and time given to workers to complete the experiment after accepting the HIT.
For example, `hit create 10 5.00 1.5` creates HITs for 10 workers, offering a $5.00 reward, and allowing each worker 1.5 hours to complete the experiment after beginning.
Creating a HIT will generate two live links: one for your ad and one for your experiment (note: the experiment link actually brings you to the full list of available experiments. Type in any of your `psiturk_keywords` from `exp config.txt` to search for your experiment). You can view these links at any time with `hit list`.
To view how many workers have completed your experiment, type `worker list`.
To accept individual workers' HITs, type `worker approve assignment_id`. To accept all workers' HITs, type `worker approve --hit hit_id`. Replace `assignment_id` or `hit_id` with the corresponding string.  See https://psiturk.readthedocs.io/en/latest/command_line/worker.html#worker-approve for documentation on `worker` commands
To end data collection before all your posted HITs have been used and remove any unused HITs, type `hit expire --all` to end the HIT availability period. Then, type `hit dispose --all` to remove the HITs from MTurk.


## Accessing and Downloading Data

As workers complete your experiment, data will populate the repository's `data/db` directory, since it is bind-mounted to the `efficient-learning-khan_db_1` image. You can view the MySQL database containing the data from a web browser using Adminer.
To view the data, first make sure the Adminer container is running with `docker start efficient-learning-khan_adminer_1` (from your local system). Open a web browser and go to `localhost:8080`. On the login screen, enter the user, password, and database name specified in `docker-compose.yml`. Select the file you want to view, and hit "View Data". You can then download the data as a number of file types.


## Troubleshooting Notes

* Recent versions of Google Chrome do not allow loading HTTP content, and thus cannot run many PsiTurk experiments. Additionally, adding Chrome to `browser_exclude_rule` in `exp/config.txt` often excludes other browsers inadvertently. If your experiment does not run on recent Chrome releases and excluding Chrome excludes other browsers during testing, add a note to your ad about the compatibility issue for workers. Workers who accept the HIT but cannot view the experiment due to compatibility issues will show a blank value in the `datastring` column and a value of `1` in the `status` column of the database when viewed in Adminer.
* After building the images, the MySQL server image will take a minute to begin communicating through its assigned port. If you get an error starting the PsiTurk server shortly after building the images, wait a minute and try again before other troubleshooting.
* If you change `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, or `MYSQL_PASSWORD` in `docker-compose.yml` after building the docker images, you may get the error `gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>` when trying turn the PsiTurk server on. Remove the images with `docker-compose rm -v`, **delete the bind-mounted data/ folder on your local machine**, and rebuild the images with `docker-compose up -d`. **NOTE**: this will delete any data you've already collected, so if you have already posted HITs, save your data first!
* Turn off your ad-blocker when testing to make sure it is not interfering with the experiment.
* Setting `us_only` to `true` and `approve_requirement` to `95` in `exp/config.txt` helps avoid strange/low-quality datasets from bots and MTurk "farms" trying to take advantage of the platform.


## Additional Reference

For more information on incorporating the NGNIX, Adminer, and MySQL components, refer to the package below:
* psiturk-docker: https://github.com/mvdoc/psiturk-docker
