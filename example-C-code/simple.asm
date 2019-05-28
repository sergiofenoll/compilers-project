
li $t0, 10
sw $t0, -4($sp)
lw $t0, -4($sp)
mul $t0, $t0, 2
sw $t0, -8($sp)
lw $t1, -8($sp)
div $t1, 2
sw $lo, -12($sp)
