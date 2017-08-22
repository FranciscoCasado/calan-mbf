function [ yy ] = fft4(x)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
j = 1i;
W = [1 -j -1 j];
y = cell(4);

% 1st stage:
for j = 1:4
    y{1,j} = x{1,j} + W(1)*x{3,j};
    y{2,j} = x{2,j} + W(1)*x{4,j};
    y{3,j} = x{1,j} + W(3)*x{3,j};
    y{4,j} = x{2,j} + W(3)*x{4,j};
end

% 2nd stage
yy = cell(4);
for j = 1:4
    yy{1,j} = y{1,j} + W(1)*y{2,j};
    yy{3,j} = y{1,j} + W(3)*y{2,j};
    yy{2,j} = y{3,j} + W(2)*y{4,j};
    yy{4,j} = y{3,j} + W(4)*y{4,j};
end

end

