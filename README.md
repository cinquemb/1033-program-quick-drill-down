1033-program-quick-drill-down
=============================

 Script that generates a JSON file that contains the most expensive item (and more descitive name pulled from armyproperty.com) for each county for each state listed in https://github.com/TheUpshot/Military-Surplus-Gear/commits/master/1033-program-foia-may-2014.csv, along with other related data.


# To Run For Yourself #
```
1) $ git clone https://github.com/cinquemb/1033-program-quick-drill-down.git
2) $ cd ../path/to/1033-program-quick-drill-down/
3) $ virtualenv env --distribute
4) $ source env/bin/activate
5) $ pip install -r ops/requirements.txt
6) $ python foia-may-2017.py
```

# Notes #

Use something like [json.human](http://marianoguerra.github.io/json.human.js/) to read the data in a quick way.
