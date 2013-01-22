(function(){ window.JST || (window.JST = {}) 
window.JST["example"] = function(obj){
var __p='';var print=function(){__p+=Array.prototype.join.call(arguments, '')};
with(obj||{}){
__p+='<p>This project is is running with the following settings:</p>\n\n<pre>\n'+
( config )+
'    \n</pre>\n\n<p>This text is rendered from a template found at <code>'+
( template_path )+
'</code>.</p>\n';
}
return __p;
};

})();