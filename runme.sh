#!/bin/bash

nohup python3 twitch_tut.py

nohup python3 restapi.py &

cd ./dndpage

serve -s build