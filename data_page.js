function data_set_selecter() {
  var x = document.getElementById("data_sets").value;
  console.log(x);
}

function colab_links()
//function that changes the google colab links based on which data set is selected.
{
  var x = document.getElementById("data_sets").value;
  if (x=="foam slice")
  {
    var url = 'https://colab.research.google.com/drive/1_MztlsaGc3bXYQqM4_bgz6_sdS5kEFX4?usp=sharing';
    window.open(url, "_blank");
  }
  if (x=="3D Rabbit")
  {

  }
  if (x=="other")
  {

  }
}

function cloud_lab_links()
//function that changes the cloud lab link based on which data set is selected.
{
  var x = document.getElementById("data_sets").value;
  if (x=="foam slice")
  {
    //var url = '';
    //window.open(url, "_blank");
  }
  if (x=="3D Rabbit")
  {

  }
  if (x=="other")
  {

  }
}

function locally_files()
//function that changes file that is downloaded based on which data set is selected.
{
  var x = document.getElementById("data_sets").value;
  var url;
  if (x=="foam slice")
  {
    url = 'demo_slice_foam_dataset_from_cloud_sources.ipynb'
    window.open(url)
  }
  if (x=="3D Rabbit")
  {

  }
  if (x=="other")
  {

  }
}
