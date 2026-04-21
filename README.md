IP address for our pi: 10.159.66.179
To ssh in: fri@ip
password: beststream


To Update the Github repository with the new code do the following: 
- In the terminal, type each of these commands: 
    git add .
    git commit -m "replace this text inside the quotes with a small message about what changes you made"
    git push
- This should give you a message saying it worked.

To SSH into the raspi: 
- Open a terminal and type in ssh fri@10.159.67.171
- Type in git clone and copy and paste the HTTPS link from GitHub that you get when you click the green "Code" button
    - here's the link if you can't find it: https://github.com/CupcakesK15/Group3_ReactionWheel_Sp26.git (this can be found in the ReadMe on the github in the master branch -> navigate to master by clicking the button right above the files that says "main" with a little fork looking thing and then click master in the drop down)
    - This should work. Hopefully. If not, then uhhh whoops
    - It'll prompt you for your username and password (probably)
- Before coding, you need to switch branches: 
    - git switch master (this command will switch)
- YOU CAN CODE IN THE TERMINAL ITSELF: 
    - Few commands: 
        - ls -a (list all stuff, including hidden files)
        - cd foldername (navigates into the folder, replace foldername with .. to go up one folder)
        - python3 filename (runs the code)
        - ctrl+c (force stops the program)
        - nano filename (allows you to edit the file)
            - while in nano: 
                - ctrl + 0 to save and hit enter to confirm
                - ctrl + x to exit nano (you need to exit after editing to run the code)
- After finishing, UPDATE THE GITHUB --> EVEN IF YOU BROKE EVERYTHING
            

If you have VSCode on a laptop set up and want to ssh in do this: 
- Click the symbol in the bottom left corner of the vscode window that has the two arrow head thingies (>< type of thing)
- Click connect to host at the top of the list from the drop down from the search bar
- Type in fri@10.159.67.171 (ignore the number at the top, not accurate)
- When it prompts for password, type in beststream (all lowercase, no spaces)
- Click Open Folder, the folder is called Group3_ReactionWheel_SP26 (should be in the fri folder or something like that)
    - it might prompt for the password again
- 