
for i in range(16,64):
	print()
	print("/* W[{:2d}] */".format(i))
	firstLine  = "sigma0 sigma0_{:2d}(W[{:2d}], output_sigma0[{:2d}]);".format(i, i-15, i)
	secondLine = "sigma1 sigma1_{:2d}(W[{:2d}], output_sigma1[{:2d}]);".format(i, i-2, i)
	lastLine   = "assign W[{:2d}] = output_sigma1[{:2d}] + W[{:2d}] + output_sigma0[{:2d}] + W[{:2d}];".format(i, i, i-7, i, i-16)
	print(firstLine)
	print(secondLine)
	print(lastLine)
