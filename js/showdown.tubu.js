(function(){
  var tubu = function(converter) {
    return [
        { type: 'lang', regex: '@icon-fa\\(([\\w\-]+)\\)', replace: '<i class="fa fa-$1">' },
        { type: 'lang', regex: '@icon-bs\\(([\\w\-]+)\\)', replace: '<span class="glyphicon glyphicon-$1"></span>' }
    ];
  };

  // Client-side export
  if (typeof window !== 'undefined' && window.showdown && window.showdown.extensions) {
    window.showdown.extensions.tubu = tubu;
  }
  // Server-side export
  if (typeof module !== 'undefined') module.exports = tubu;
}());
