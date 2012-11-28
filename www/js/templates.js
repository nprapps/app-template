this["JST"] = this["JST"] || {};

this["JST"]["example"] = function(obj){
var __p='';var print=function(){__p+=Array.prototype.join.call(arguments, '')};
with(obj||{}){
__p+='This text is rendered from an example template named <strong>'+
( name )+
'</strong>.\n';
}
return __p;
};