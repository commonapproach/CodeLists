<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Poppins">
<meta charset="utf-8" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-FMBZVRDNYK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-FMBZVRDNYK');
</script>
<style>
@import url('https://fonts.googleapis.com/css?family=Poppins');
#headline {
    font-family: 'Poppins';
    font-weight: bold;
    font-size: 48px;
    text-align: center;
//    color: #a7d86d;
    color: #6ca7e0;
    display: inline-block;
    margin: auto;
    width: 100%;
}
button {
 font-family: 'Poppins';
 font-weight: bold;
 font-size: 24px;
 //background-color: #a7d86d;
 background-color: #6ca7e0;
 color: #EEEEEE;
 padding: 10px;
 float: right;
 text-align: center;
 text-decoration: none;
 margin: 4px 1px;
 border-radius: 85%;
 border: 0px;
}
#topbanner {
 height: 100%;
 width: 100%;
 display: inline-block;
}
#codelist-table {
 width: 95%;
 margin: auto;
 padding-top: 30px;
}

.atable  {
 width: 95%;
 margin: auto;
 padding-top: 30px;
}

th {
 background-color: #6ca7e0;
 line-height: 24px;
 font-weight: bold;
 border-right: solid 2px #6ca7e0;
 border-left: solid 2px #6ca7e0;
}
table { border-collapse: collapse;
border-radius: 6px;
-moz-border-radius: 6px;
 border-spacing: 2px;
}
tr { border: none; }
td {
  border-right: solid 2px #6ca7e0;
  border-left: solid 2px #6ca7e0;
  border-top: solid 2px #6ca7e0;
  border-bottom: solid 2px #6ca7e0;

}
</style>
<title>Common Approach Code List Server</title>
</head>
<body>
<div id="topbanner">
<button id="aboutbutton" class="button">About</button><button id="buttonfaq" class="button">FAQ</button>
</div>
<div id="headline">Common Approach Code List Server</div>

<?php

# This code generates a table of Codelists with links to each of their formats,
# and a description, as defined below.

$codelists = [
  'CanadianCorporateRegistries' => '',
  'EquityDeservingGroupsESDC' => 'A codelist vocabulary of Equity Deserving Groups as defined by Ministry of Employment and Social Development of Canada.',
  'ESDCSector' => '',
  'FundingState' => 'A codelist vocabulary of FundingStates. (<a href="FundingStateExample.ttl">Example</a>)',
  'ICNPOsector' => 'This list represent a possible categorization of sectors as defined by the International Classification of Nonprofit Organizations and republished by Common Approach to Impact Measurement as an RDF codelist.',
  'IRISImpactCategory' => 'IRIS+ is the generally accepted system for measuring, managing, and optimizing impact. This Cost List is an implementation of the GIIN IRIS+ System metrics in an RDF data model.',
  'IRISImpactTheme' => 'IRIS+ is the generally accepted system for measuring, managing, and optimizing impact. This Cost List is an implementation of the GIIN IRIS+ System metrics in an RDF data model.',
  'IrisMetric53' => 'IRIS+ is the generally accepted system for measuring, managing, and optimizing impact. This Cost List is an implementation of the GIIN IRIS+ System metrics in an RDF data model.',
  'LocalityStatsCan' => 'A codelist vocabulary of Locality Codelists according to Statistics Canada definitions.',
  'OrgTypeGOC' => 'A codelist vocabulary of organization types informed by Government of Canada definitions.',
  'PopulationServed' => 'A codelist vocabulary of Populations Served.',
  'ProvinceTerritory' => 'A codelist vocabulary of Province and Territory Codelists according to Statistics Canada definitions.',
  'RallyImpactArea' => '',
  'SDGImpacts' => 'A codelist vocabulary of Sustainable Development Goals (SDGs) Taxonomy of Impact Themes',
  'SELI-GLI' => 'Social Equity and Gender-Lens Investment Assessment',
  'StatsCanSector' => 'This list represent a possible categorization of sectors as defined by Statistics Canada and republished by Common Approach to Impact Measurement as an RDF codelist.' ,
  'UnitsOfMeasureList' => '',
];

$formats = [
  'rdf/xml' => '.owl',
  'turtle'  => '.ttl',
  'json-ld' => '.jsonld',
  'triples' => '.nt',
  'csv'     => '.csv',
];

## This is the table header, in plain HTML
?>
<div id="headline">Common Approach Code List Server</div>
<table id="codelist-table">
 <tr style="!important; color:#000000;empty-cells:show;">
  <th style="width:35%; text-align: center;">Name</th>
  <th style="width:325px;">Description</th>
  <th style="width:10%; text-align: center;">Last Update</th>
  <th style="width:10px; text-align: center;">Issues</th>
 </tr>
<?php

# Iterate over defined codelists, building a table row for each.
foreach ($codelists as $list => $description) {

  # Build line of links for each format
  $links = sprintf('<strong>%s</strong> (', $list);
  foreach ($formats as $format => $extension) {
    $links .= sprintf('<a href="%s%s">%s</a> / ', $list, $extension, $format);
  }
  # Remove trailing / and space from last iteration above
  $links = rtrim($links, " /");
  $links .= sprintf(')');

# Now we go back to plain HTML, to emit the table row with our computed values.
?>
 <tr>
  <td><?= $links ?></td>
  <td><?= $description ?></td>
  <?php # @TODO: Make this dynamic? Either add date to the codelists dictionary above, look in the file for dcterms:date, or scan the filesystem for timestamp? ?>
  <td style="text-align: center;">Dec 1, 2025</td>
  <td style="text-align: center;">0</td>
 </tr>
<?php
}
# And close out the file with footer/closing HTML.
?>
</table>
<div style="margin-bottom:10px;"></div>
<table id="mytable1" class="atable">
 <tr style="!important; color:#000000;empty-cells:show;">
  <th style="text-align: center;">Documentation</th>
 </tr>
 <tr><td> </td></tr>
 </table>
</body>
</html>
