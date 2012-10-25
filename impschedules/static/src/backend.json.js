this.recline = this.recline || {};
this.recline.Backend = this.recline.Backend || {};
this.recline.Backend.json = this.recline.Backend.json || {};

(function($, my) {
  my.__type__ = 'json';

  my.fetch = function(dataset) {
    var dfd  = $.Deferred(); 
    var url = dataset.url;

      $.getJSON(url, function(d) {
        var result = d.dates;
        var fields = dataset.fields;
        dfd.resolve({
          records       : result,
          fields        : dataset.fields,
          useMemoryStore: true
        });
      });

    return dfd.promise();
 };


}(jQuery, this.recline.Backend.json));
