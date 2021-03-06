<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. leven-squash</a></li>
<li><a href="#sec-2">2. About</a>
<ul>
<li><a href="#sec-2-1">2.1. Approach</a></li>
<li><a href="#sec-2-2">2.2. LevenSquash</a></li>
<li><a href="#sec-2-3">2.3. Correction Factor</a></li>
<li><a href="#sec-2-4">2.4. Similarity metric</a></li>
</ul>
</li>
<li><a href="#sec-3">3. Usage</a>
<ul>
<li><a href="#sec-3-1">3.1. levensquash</a>
<ul>
<li><a href="#sec-3-1-1">3.1.1. LevenSquash</a></li>
</ul>
</li>
<li><a href="#sec-3-2">3.2. demo</a>
<ul>
<li><a href="#sec-3-2-1">3.2.1. ranges</a></li>
</ul>
</li>
</ul>
</li>
</ul>
</div>
</div>

# leven-squash<a id="sec-1" name="sec-1"></a>

A compression heuristic implementation for approximating string distance + some analysis and a similarity metric idea.

# About<a id="sec-2" name="sec-2"></a>

The Levenshtein distance of two strings is the smallest number of single character edits &#x2013; insertions, deletions, or substitutions &#x2013; needed to transform one string to the other. The complexity of this problem, with strings of length n and m, is O(n\*m), and therefore can be prohibitively slow for very long strings. There are several algorithmic approaches to limiting the complexity of the problem with near-linear approximate string matching (ASM).

## Approach<a id="sec-2-1" name="sec-2-1"></a>

Consider all neighborhoods of length N of the source strings, and hash them to random 64-bit values. Given a compression factor, C, each neighborhood hash is converted to a character and output with approximate probability 1/C. Equivalent string neighborhoods must hash to equivalent values. The result is a signature roughly 1/C times the length of the source string that preserves the source string's characteristics. 

This idea is presented in a [blog post by Peter Coates](https://hadoopoopadoop.com/2016/02/12/super-fast-estimates-of-levenshtein-distance/)

## LevenSquash<a id="sec-2-2" name="sec-2-2"></a>

The process:

(i) Let P, the current position, be initially zero.
(ii) Compute H(P), the hash of the N-sized substring starting at P.
(iii) If H(P) modulo C is non-zero, generate no output. If not at the end, increment P and return to step #1.
(iv) Otherwise, output a pseudo-random character from the pool of possible signature characters in such a way that the choice is highly random, but a given hash will always result in the same character.
(v) If not at the end, increment P and go to step #1.
(vi) Else, finish.

The output strings of this procedure are the two signatures, of approximately 1/C times the length of their respective source's length, for which are computed true Levenshtein distance. This has a time complexity of O(n\*m/C<sup>2</sup>), a C<sup>2</sup> improvement over a true calculation. There are several factors in this process: (1) the hash implementation to be used on each of the K neighborhoods, which should be near-uniform. (2) the method for selecting characters for the signature to represent a given neighborhood, which provides output with 1/C frequency, and the alphabet from which these characters are selected. (3) the value of N, which defines the size of the neighborhoods to be hashed, and also describes the sensitivity of the process to minor differences. (4) the value of C, which defines the factor by which the signature will be smaller than the source string.

For (1), several differrent hashing methods are used, and found a CRC hashing implementation worked fastest and provided an acceptable distribution of characters. The character selection process described in (2) seems to be mostly invariable. The length of the alphabet chosen, however, proves to contribute critically to the derived correction factor. The values for N and C, described in (3) and (4), have interesting contributions to the process, which are discussed in the following section.

## Effects of C and N

The contributions of C and N to the process where not entirely obvious. To produce an appropriate data set, a program was written to collect the files in a directory, read them, and produce all possible pair combinations. 

In this instance, a directory with 15 full­sized books was used, each book ranging in length from ~155k to ~170k characters of ASCII text. These 15 books produce 105 combinations, and therefore 105 distance evaluation sets. For each set, Levenshtein distance was calculated as well as estimations using a range of N and C values, N from 1 to 40 in increments of one, and C from 100 to 200 in increments of 10. 

The results were useful for producing a set of statistics from which were found the followi about N (C isn't very interesting): an optimal value of N was 6. 

Of the 390 estimations on 105 different string pairs (a total of 40,950 estimations), the mean value of N for the top 1,000 estimations was 5. The lowest mean estimate errors are provided by 6 ≤ N ≤ 10, much smaller than those provided by N in the range of 3 to 5. Interestingly, 3 ≤ N ≤ 5 gives the best estimates, but with very high variance. And so, this behavior for small N appears similarly at the high end of errors, where the worst 1,000 error results are also predominantly provided by N ≤ 5. We suspect the explanation for this discrepancy is related to the less­than­random signatures that very low values of N encourage (this discussed a bit more below), which results in a very large standard distribution for their errors. 

## Correction Factor<a id="sec-2-3" name="sec-2-3"></a>

It might seem that the simply scaling the signature distance calculation by the compression factor, C, would provide the estimate. However, because the signatures are more random (i.e., are of higher entropy) than source strings, we can expect their respective normalized distances to be greater. In fact, the average distance between English text, normalized, is ~0.784. This figure was produced by taking the average of 10,000 different distance calculations of English character strings 10,000 in length. The average distance for random strings picked uniformly from an alphabet of size 62, is ~0.946 &#x2013; much larger. 

Therefore, assuming that signatures are near-random, we can assume that estimates, on average, are slightly larger than the exact calculation, and should be corrected by factor proportional to the ratio, ~0.829. 

This idea would only seem reasonable provided the estimate is calculated with appropriate values of N; because the value of N essentially defines the pattern size of text we wish to encode in the source. With N chosen too small, patterns become distributed decreasingly uniformly. For example, an N of size 8 will characterize the source string in terms of length 8 patterns, which we can figure are distributed much more uniformly than length 1 patterns (e.g., the pattern "tern wil" will likely only appear once in this text, while the pattern "e" will appear many times, predictably more than the pattern "l", which will appear predictably more than the pattern "z").

To affirm the assumption that average distance between signatures is very similar to the average distance of random strings (i.e., signatures are near-random), tests were run over 10,000 signatures produced from 10,000 random strings of English text. As shown by the results over values of N=1 to N=40, the average distance is about equal to 0.95 for N ≥ 6, suggesting that corresponding signatures are distributed about uniformly for those N values. For 3 < N ≤ 6, average distance was ~0.91. For values of N < 3, distribution was uselessly non-uniform.

A result of this fact is that larger N make for estimates with higher mean values. 

Using the correction factor produced with this result on a set of 105 large files yielded an average estimation error improvement of 470% with 0 failed corrections (i.e., corrections that mistakenly have greater error than the non-corrected version). The code used for this lives in leven-squash/demo.

## Similarity metric<a id="sec-2-4" name="sec-2-4"></a>

A typical alphabet size used for output signatures was alphanumerics, 62 characters in length. For common C, say, 100, this means that a source string length 100,000 will compress to a signature of length ~1,000, and will, assuming a uniform distribution, have on average each output character repeated about 16 times in the signature. Of course, many, perhaps all, of the ~16 instances of a particular output character in the signature correspond to different patterns in the source, i.e., are hash collisions. 

The idea behind the similarity metric adaptation of this heuristic is as follows: creating a very large alphabet to minimize these types of collisions ensures a very high probability that a given character in the signature represents exactly one pattern in the input. Therefore, producing character counts of two signatures, and then the cosine between these character counts, would yield a measure of similarity of the two signatures, and therefore also of the two source strings. This measure would also handle text "scrambling" (which levenshtein distance does very poorly). This technique works well, as implemented roughly in 'levenshtein.similarity', however it suffers certain problems:

1.  C is not important. The value of C is not important because C is merely the factor by which we want to reduce the length of the source in the signature. Because cosine, like compression, is a linear operation, minimizing the length of the signatures introduces error unjustified by speed improvement.
2.  N is difficult to determine. The pattern size we want to recognize is difficult to say definitively, and varies from input to input. The use case for this method is recognizing the scrambling of strings, so determining an optimal N is not obviously possible on a per-use basis.

Some research suggests that C being unimportant seems to reduce this process to a sort of n-gram comparison. So unfortunately this idea turned out to reduce to a process that turned out to not be new.

## Conclusion

With an implementation of leven­squash, an algorithm for estimating Levenshtein distance, sets of results were produced to characterize parameters N and C, compression neighborhood size and factor. An optimal range for these parameters was found. Additionally entropy considerations were used to greatly improve the accuracy of the estimations. A derivative concept was explored for a similarity metric, and found it to be effective but likely already known. 

Areas of continued interest and exploration are: deeper research into known implementations and alternatives of the proposed similarity metric; the odd distributions for low values of N and why they occur. 

# Usage<a id="sec-3" name="sec-3"></a>

## levensquash<a id="sec-3-1" name="sec-3-1"></a>

### LevenSquash<a id="sec-3-1-1" name="sec-3-1-1"></a>

To compute the approximate LD with N=10, C=140, run the following.

```python
from levenshtein.leven_squash import LevenSquash
    
comp = Compressor(compression=CRCCompression(), C=140, N=10)
    
long_string1 = "foo"
long_string2 = "bar"
    
ls = LevenSquash(compressor=comp)
    
est = ls.estimate(longStr1, longStr2)
```

To produce the corrected distance:

```python
est_corrected = ls.estimate_corrected(long_str1, long_str2)
```

The actual true distance is available:

```python
true = ls.calculate(long_str1, long_str2)
```

There is a SmartLevenSquash module, a wrapper for LevenSquash. It caches results and produces information like computation time.

## demo<a id="sec-3-2" name="sec-3-2"></a>

### ranges<a id="sec-3-2-1" name="sec-3-2-1"></a>

Runs tests for ranges N=n1-n2, C=c1-c2 in steps of step c, step n. Tests are performed on all non-redundant pairs of files in 'directory'. 

```python
from ranges import *
    
n1 = 2
n2 = 10
c1 = 100
c2 = 150
step_c = 10
step_n = 1
    
name = "my_cool_test"
d = "dir_with_text_files"
r = "dir_for_results"
    
test_and_save(name, directory=d, results_dir=r)
    
results = load_test_results(name, r)
```

Results is a list of range(n1, n2) \* range(c1, c2) sublists. Each sublists contains exactly results for each of the file pairs, for a total of num<sub>pairs</sub> results in a sublist. These sublists are ordered such that lowest error is first. That is, the lowest error produced for each of the files pairs is stored in as the first sublist, the second lowest errors are in the second sublist, etc. They have the following structure:

```python
pp.pprint(results[0][0])
```

Has the following output

    ((0.034853, 140, 5), "some_file__AND__some_other_file")

The next element in the sublist will have larger error.

```python
pp.pprint(results[0][1])
```

The next smallest error, packaged with the corresponding C and N value, and the file operated on.

    ((0.04221, 110, 6), "a_third_file__AND__some_other_file")

Use stat(results) to squash the sublists into statistical results. So stats[i] returns a set of statistics on sublist results[i]:

```python
stats = stat(results)
    
pp.pprint(stat[0])
```

Output, for example,

    (1,
     {'MAX':    {'C': 190, 'ERROR': 0.034703203554769815,  'N': 10},
      'MEAN':   {'C': 138, 'ERROR': 0.0094129152080824,    'N': 4},
      'MEDIAN': {'C': 130, 'ERROR': 0.00714506625641351,   'N': 4},
      'MIN':    {'C': 100, 'ERROR': 6.275395742143989e-05, 'N': 2},
      'RANGE':  {'C': 90,  'ERROR': 0.034640449597348376,  'N': 8}})

This data structure can be flattened, filtered, unzipped, etc, to be analyzed. It was called on directories with 15 full-sized book text documents, for a total of 105 file pair. The ranges for N and C were n1=2, n2=40, c1=100, c2=200, with c and n stepping in 10, 1, respectively, for a total of 390 N and C value pairs. This amounted to ~40,000 estimations.
