import javax.crypto.spec.PBEKeySpec;

public class ConstructPBEKeySpec{
   public void pattern(char[] password, byte[] salt, int keylength) {
	PBEKeySpec pks = new PBEKeySpec(password, salt, 15000, keylength);	
   }
}
