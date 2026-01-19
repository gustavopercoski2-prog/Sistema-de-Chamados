package com.chamados.auth_api.utils;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;
import java.util.Base64;

public class DjangoPasswordHasher {

    // O algoritmo que o Django usa
    private static final String ALGORITHM = "pbkdf2_sha256";

    public boolean checkPassword(String rawPassword, String storedPassword) {
        String[] parts = storedPassword.split("\\$");
        
        // Verifica se é o formato padrão do Django (algoritmo$iterações$salt$hash)
        if (parts.length != 4) {
            return false; 
        }

        Integer iterations = Integer.parseInt(parts[1]);
        String salt = parts[2];
        String hash = parts[3];

        String computedHash = getEncodedHash(rawPassword, salt, iterations);
        
        return hash.equals(computedHash);
    }

    private String getEncodedHash(String password, String salt, int iterations) {
        try {
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt.getBytes(), iterations, 256);
            SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            byte[] hash = skf.generateSecret(spec).getEncoded();
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new RuntimeException("Erro ao processar hash de senha", e);
        }
    }
}