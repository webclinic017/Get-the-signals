This is my first Flask project (Python, Bootstrap, HTML, CSS,...). The aim is to build a web app that connects to different API's. 
It will gather data from diverse web sources, synthesize and display the competitive arenas for every chosen stock.
The app is connected to various sqlite databases.
The app integrates a user authentication procedure.


<h4> Command to create virtual env (VS code, Ubuntu 20) </h4>
<p>In <strong>project root dir</strong> open command line:</p>

```
python3 -m venv .sversus
source .sversus/bin/activate
sudo apt-get install libsqlite3-dev
```

To initiate db, run:

```python3 db_create.py```

<h4> To be implemented </h4>

<ul>
    <li>Page with macro-economic information (bokeh figures)</li>
    <li>Connect DB to external API to gather economic data</li>
    <li>Containerize automated web scraping process, deploy to AWS lambda, and link it to the website through an API</li>
    <li>Detect all minimas for a chosen stock and give the ability to download a csv with flagged positions</li>
    <li>Detect double & tripple bottoms & tops</li>
</ul>

![alt-text](screencaps/home.PNG)
![alt-text](screencaps/registration.PNG)
![alt-text](screencaps/table.PNG)


<h4>Personnal issues encountered and turnaroud:</h4>

<p>https://stackoverflow.com/questions/57018186/cant-activate-environment-from-visual-studio-code</p>

<ul>
	<li>ctrl + shift +p find the settings.json, append two rows: "python.terminal.activateEnvironment": true, "terminal.integrated.shell.windows": "C:\WINDOWS\System32\cmd.exe",</li>
	<li>choose to run the task in the terminal</li>
</ul>


<h4> Regarding general DB alimentation </h4>

While being in the folder containing the data to upload (```Overview.csv``` in this case), connect to the remote MySQL db with terminal and execute a command like the following: </br>
<code>LOAD DATA LOCAL INFILE 'Overview.csv'INTO TABLE financetest COLUMNS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;</code>

