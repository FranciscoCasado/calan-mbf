close all
t = 0:1:3600;
wave = sin(pi/180*t);

x = cell(4); % cell array containing the wave from each element

shift_x = 30;
shift_y = 34;
offset = 1;
inc = 360;

for i = 1:4
    for j = 1:4
        start = shift_x*(i-1)+shift_y*(j-1)+offset;
        x{i,j} = wave(start:start+inc);
    end
end


% Azimut
y = fft4(x);
% Elevation
yy = fft4(y');

% re-arrange
Y = cell(3);
ind = [4 1 3];
for i = 1:3
    for j = 1:3
        Y{i,j} = yy{ind(i),ind(j)};
    end
end
%Y = yy;
% plot stuff
%fig_dbf = figure;
%fig_dbf.Position = [6 3 4 3];
[width,length] = size(Y);
[I,J] = meshgrid(1:width,1:length);
power = sqrt(array_power(Y));
%surf(I-2,J-2,power)

fig_slice = figure;
for i = 1:width
    subplot(width,1,i)
    bar(0:2,power(i,:))
end

