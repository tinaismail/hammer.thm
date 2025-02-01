# hammer.thm
Resources I used to solve the THM Hammer room


## Add target to etc/hosts
```
echo target hammer.thm >> etc/hosts
```

## Scan open ports
`nmap -p- hammer.thm`

Open browser and navigate to hammer.thm:1337

## Gobuster directory bruteforcing
```
gobuster -u http://hammer.thm:1337 -w Tools/wordlists/dirbuster/directory-list-1.0.txt dir
```
## Sed to substitute hmr_ at the beginning of each directory in the list
```
cp Tools/wordlists/dirbuster/directory-list-1.0.txt list.txt
```
then
```
sed -i 's/^/hmr_/' list.txt
```

## Use script.py to enumerate 
Challenges: The session ID has a timeout of 5 requests, so I had to keep regenerating session IDs with a POST request to index.php every 5 requests

There will be multiple VALID codes, just keep an eye on the terminal until one pops up and use it



