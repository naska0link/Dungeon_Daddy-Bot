#!/bin/bash

python3 twitch_tut.py

python3 restapi.py &

cd ./dndpage

serve -s build