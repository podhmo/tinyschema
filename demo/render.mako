<%namespace file="./form.mako" name="f"/>

<form action="#" method="POST">
%for field in schema:
  ${f.render_field(field)}
%endfor
</form>
