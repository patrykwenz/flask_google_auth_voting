<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="static/img/logo.png" alt="Logo">
  </a>

  <h3 align="center">Safe e - voting system</h3>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#download-repository">Download repository</a></li>
        <li><a href="#install-required-python-packages">Install required python packages</a></li>
        <li><a href="#register-application">Register application</a></li>
        <li><a href="#prepare-mongodb">Prepare MongoDB</a></li>
        <li><a href="#export-environment-variables">Export Environment Variables</a></li>
        <li><a href="#run-application">Run application</a></li>
      </ul> 
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
E - voting system based on GoogleAuth and MongoDB Cloud. 

### Built With
* [Python 3.8.3](https://www.python.org/downloads/)
* [Pycharm Professional](https://www.jetbrains.com/pycharm/download/#section=windows)
* [Opera](https://www.opera.com/pl)



<!-- GETTING STARTED -->
## Getting Started

In order to get started you have to through these steps:

### Download repository

   ```sh
   git clone https://github.com/patrykwenz/flask_google_auth_voting.git
   ```

### Install required python packages 

   ```sh
   pip install -r requirements.txt
   ```

### Register application 
  [GoogleAuth Tutorial](https://realpython.com/flask-google-login/)
  
### Prepare MongoDB 
  [MongoDB Tutorial](https://docs.atlas.mongodb.com/getting-started)

### Export Environment Variables
   ```sh
   set MONGODB_CLIENT_URI = YOUR_MONGO_URI
   ```
   ```sh
   set GOOGLE_CLIENT_ID = YOUR_GOOGLE_CLIENT_ID
   ```
   ```sh
   set GOOGLE_CLIENT_SECRET = YOUR_GOOGLE_CLIENT_SECRET
   ```
### Run application

 ```sh
   python app.py
   ```

<!-- USAGE EXAMPLES -->
## Usage
[Website](voting.ninjait.pl)

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact
[Univeristy e - mail](mailto:patryk.wenz@student.put.poznan.pl)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [ReadMe template](https://github.com/othneildrew/Best-README-Template/blob/master/README.md)
* [Google Auth Tutorial](https://realpython.com/flask-google-login/)
* [MongoDB Tutorial](https://docs.atlas.mongodb.com/getting-started)
