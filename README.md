# snax4moss

The code in this repo aims to acquire all Mössbauer spectra data from the Mt Holyoke archive:

```
https://mossbauer.mtholyoke.edu/
```

The data is organised as groups titled by a general mineralogical / origin / metal / isotope. Each group contains samples relevant to that group. A sample usually contains a single spectrum, but links in bold contain more than one. Sometimes they contain no spectra - presumably an upstream error.

Each spectrum has two files associated with it - a "datafile" and a "textfile".

Ideally, for each spectrum, we would have the following information:
• The sample name / chemical details / etc in as much detail as possible.
• The y-axis - hits / transmission.
• The x-axis - as channel numbers / ideally as velocity.
• Collection information such as sample size / thickness, temperature in K.

### Issues:

• The biggest issues is that for many / most samples, a request for the "textfile" (actual hits) returns a 500 error at the server.
• Secondly, each file tends to be named without a consistent format. Here we have looked at the first line of each downloaded file, which almost always contains a descriptive line about the sample and collection details. This would be ideal to rename the files. However, this also tends to have annoying characters in, such as %^&£$\ etc which break naming file system conventions. We can regex them out, but there are also issues with invisible control characters.
