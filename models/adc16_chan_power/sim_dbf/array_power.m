function [ power ] = array_power( x )
%UNTITLED5 Summary of this function goes here
%   Detailed explanation goes here
[rows,columns] = size(x);
power = zeros(rows,columns);
for i = 1:rows
    for j = 1:columns
        power(i,j) = mean(x{i,j}.*conj(x{i,j}));
    end
end

end

