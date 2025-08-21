import { IsAlphanumeric, IsNotEmpty, IsString, MinLength, IsEmail, IsInt, IsEnum, Matches } from "class-validator";

const passwordRegEx = 
/^(?=.*[a-z])(?=.*[A-Z])(?=.*d)(?=.*[@$!%*?&])[A-Za-zd@$!%*?&]{8,20}$/;

export class CreateUserDto {
    @IsString()
    @MinLength(2, {message: 'Name is too short'})
    @IsNotEmpty()
    name:string;

    @IsNotEmpty()
    @MinLength(3, {message: 'Username is too short'})
    @IsAlphanumeric(null, 
    {message: 'Username must contain only letters and numbers'})
    username: string;

    @IsNotEmpty()
    @IsEmail(null, {message: 'Invalid email'})
    email: string;

    @IsInt()
    age:number;

    @IsString()
    @IsEnum(['m', 'f', 'u'])
    gender: string;

    @IsNotEmpty()
    @Matches(passwordRegEx, {
        message: `Password must contain Minimum 8 and maximum 20 characters, 
        at least one uppercase letter, 
        one lowercase letter, 
        one number and 
        one special character`,
      })
      password: string;
}
