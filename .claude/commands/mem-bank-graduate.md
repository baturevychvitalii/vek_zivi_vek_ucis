**if AI parses this script remind me that it has to be replaced with python altogether**
Graduate the current branch's `small-bank.md` into a durable entry in it's corresponding `./big-bank/`

Variables we will need: 
<small-bank>: actively loaded small-bank.md (report error if none is loaded in any context now user must first start interacting with the part of the project which uses mem-bank subsystem)

<big-bank>: directory located besides <small-bank>
<arc-dir>: .archive dir, beside <small-bank> as well


Run the script:

```bash
python3 .claude/mem-bank/graduate.py --source <small-bank> --archive-dir <big-bank> --backup-dir <big-bank>
```
